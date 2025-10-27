from typing import Any
from pydantic import ValidationError, BaseModel

from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent, event_source

from bedrock_impl.bedrock import Bedrock
from bedrock_impl.store import ChatStore

import json

logger = Logger('lambda-rag', level="DEBUG")

class Response(BaseModel):
    statusCode: int
    body: str
    headers: dict[str, Any] = {
                            'Access-Control-Allow-Headers': 'Content-Type',
                            'Access-Control-Allow-Origin': '*',
                            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
                        }

@event_source(data_class = APIGatewayProxyEvent)
def bedrock_handler(event: APIGatewayProxyEvent, context: LambdaContext) -> dict[str, Any]:
    """
    AWS Lambda handler for Bedrock RAG queries.
    """
    try:
        logger.debug("Bedrock Handler started...")
        if not event.body:
            return Response(statusCode=400, body="Missing request body").model_dump()
        
        user_id = event.request_context.authorizer.claims.get("sub")
        
        if not user_id:
            return Response(statusCode=400, body="Missing cognito user ID").model_dump()
        
        bedrock = Bedrock()
        chat_store = ChatStore()

        request = bedrock.parse_request(event.body)
        logger.debug("Parsed request: ", request)

        session_id = request.session_id if request.session_id else chat_store.create_session(user_id = user_id)

        chat_store.save_message(
            role = 'user',
            body = request.content,
            session_id = session_id,
        )

        conversation = chat_store.get_latest_messages(
            user_id = user_id,
            session_id = session_id,
            n = 5
        )
        
        response = bedrock.generate_response(conversation)
        logger.debug(f"Raw response: {response}")
        response = bedrock.parse_response(response)
        logger.debug(f"Parsed response: {response}")

        chat_store.save_message(
            role = 'ai',
            body = response.content,
            session_id = session_id,
            response_parts = response.response_parts
        )

        response.session_id = session_id

        return Response(statusCode=200, body=response.model_dump_json()).model_dump()

    except ValidationError as ve:
        logger.exception("Validation error")
        return Response(statusCode=400, body=f"Validation error: {ve.errors()}").model_dump()

    except Exception as e:
        logger.error("Internal error:", e)
        return {
            "statusCode": 500,
            'headers': {
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            "body": "Internal server error"
        }

@event_source(data_class = APIGatewayProxyEvent)
def conversation_handler(event: APIGatewayProxyEvent, context: LambdaContext) -> dict[str, Any]:
    """
    AWS Lambda handler for fetching conversations (sessions).
    """

    try:
        path = event.path
        path_params = event.path_parameters or {}
        chat_store = ChatStore()
        http_method = event.http_method

        if "/messages/" in path:
            session_id = path_params.get("session_id")
            if not session_id:
                return {
                    "statusCode": 400,
                    'headers': {
                        'Access-Control-Allow-Headers': 'Content-Type',
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
                    },
                    "body": "Missing session ID"
                }

            messages = chat_store.get_messages(session_id)
            return {
                "statusCode": 200,
                'headers': {
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
                },
                "body": json.dumps([message.model_dump(mode='json') for message in messages]),
            }
        
        elif "/conversation/" in path and http_method == "DELETE":
            session_id = path_params.get("session_id")
            if not session_id:
                return {
                    "statusCode": 400,
                    'headers': {
                        'Access-Control-Allow-Headers': 'Content-Type',
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
                    },
                    "body": "Missing session ID"
                }

            messages = chat_store.delete_conversation(session_id)
            return {
                "statusCode": 200,
                'headers': {
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
                },
                "body": f"Successfully deleted conversation: {session_id}",
            }
        
        elif "/conversation/" in path:
            user_id = path_params.get("user_id")
            if not user_id:
                return {
                    "statusCode": 400,
                    'headers': {
                        'Access-Control-Allow-Headers': 'Content-Type',
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
                    },
                    "body": "Missing user ID"
                }

            conversations = chat_store.get_conversations(user_id)
            return {
                "statusCode": 200,
                'headers': {
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
                },
                "body": json.dumps([conversation.model_dump() for conversation in conversations]),
            }

        else:
            return {
                    "statusCode": 404,
                    'headers': {
                        'Access-Control-Allow-Headers': 'Content-Type',
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
                    },
                    "body": "Not found"
                }
    
    except ValidationError as ve:
        logger.error("Validation error:", ve)
        return {
            "statusCode": 400,
            'headers': {
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            "body": "Bad request"
        }

    except Exception as e:
        logger.error("Internal error:", e)
        return {
            "statusCode": 500,
            'headers': {
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            "body": "Internal server error"
        }
