from typing import Any
from pydantic import ValidationError

from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent, event_source

from bedrock_impl.bedrock import Bedrock
from bedrock_impl.store import ChatStore

logger = Logger('lambda-rag')

@event_source(data_class = APIGatewayProxyEvent)
def bedrock_handler(event: APIGatewayProxyEvent, context: LambdaContext) -> dict[str, Any]:
    """
    AWS Lambda handler for Bedrock RAG queries.
    """
    try:
        if not event.body:
            return {
                "statusCode": 400,
                "body": "Missing request body",
                'headers': {
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
                },
            }
        
        user_id = event.request_context.authorizer.claims.get("sub")
        
        if not user_id:
            return {
                "statusCode": 400,
                'headers': {
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
                },
                "body": "Missing cognito user ID"
            }
        
        bedrock = Bedrock()
        chat_store = ChatStore()

        request = bedrock.parse_request(event.body)

        session_id = request.session_id if request.session_id else chat_store.create_session(user_id = user_id)

        chat_store.save_message(
            role = 'user',
            body = request.content,
            session_id = session_id,
        )

        query_context = chat_store.get_latest_messages(
            user_id = user_id,
            session_id = session_id,
            n = 5
        )
        
        response = bedrock.generate_response(request.content, query_context)
        response = bedrock.parse_response(response)


        chat_store.save_message(
            role = 'ai',
            body = response.content,
            session_id = session_id,
            response_parts = response.response_parts
        )

        response.session_id = session_id

        return {
            "statusCode": 200,
            'headers': {
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            "body": response.model_dump_json()
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