from typing import Any
from pydantic import ValidationError

from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent, event_source

from bedrock_impl.src.bedrock import Bedrock
from bedrock_impl.src.store import ChatStore

logger = Logger('lambda-rag')

@event_source(data_class = APIGatewayProxyEvent)
def bedrock_handler(event: APIGatewayProxyEvent, context: LambdaContext) -> dict[str, Any]:
    """
    AWS Lambda handler for Bedrock RAG queries.
    """
    try:
        if not event.body:
            return {"statusCode": 400, "body": "Missing request body"}
        
        user_id = event.request_context.authorizer.claims.get("sub")
        
        if not user_id:
            return {"statusCode": 400, "body": "Missing cognito user ID"}
        
        bedrock = Bedrock()
        chat_store = ChatStore()

        request = bedrock.parse_request(event.body)

        session_id = request.session_id if request.session_id else chat_store.create_session(user_id = user_id)

        chat_store.save_message(
            role = 'user',
            body = request.query,
            session_id = session_id,
        )

        query_context = chat_store.get_latest_messages(
            user_id = user_id,
            session_id = session_id,
            n = 5
        )
        
        response = bedrock.generate_response(request.query, query_context)
        response = bedrock.parse_response(response)


        chat_store.save_message(
            role = 'ai',
            body = response.answer,
            session_id = session_id,
            response_parts = response.response_parts
        )

        response.session_id = session_id

        return {
            "statusCode": 200,
            "body": response.model_dump_json(),
        }

    except ValidationError as ve:
        logger.error("Validation error:", ve)
        return {"statusCode": 400, "body": "Bad request"}

    except Exception as e:
        logger.error("Internal error:", e)
        return {"statusCode": 500, "body": "Internal server error"}