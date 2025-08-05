from typing import Any
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools import Logger
from model import QuestionRequest, AnswerResponseBody, ApiGatewayResponse
from pydantic import ValidationError
import boto3
from mypy_boto3_bedrock_agent_runtime.type_defs import RetrieveAndGenerateResponseTypeDef

logger = Logger(service="lambda-rag", level="DEBUG")

# curl -X POST https://kvn5jcez6e.execute-api.us-east-1.amazonaws.com/Prod/rag/bedrock -d '{"query": "What is the content platform?"}'

def bedrock_handler(event: dict[str, Any], context: LambdaContext) -> dict[str, Any]:
    try:
        client = boto3.client('bedrock-agent-runtime')

        request = QuestionRequest.model_validate_json(event["body"])

        bedrock_response: RetrieveAndGenerateResponseTypeDef = client.retrieve_and_generate(
            input={"text": request.query},
            retrieveAndGenerateConfiguration={
                "knowledgeBaseConfiguration": {
                    "knowledgeBaseId": "XBOBJWN1MQ",
                    "modelArn": "anthropic.claude-3-5-sonnet-20240620-v1:0"
                },
                "type": "KNOWLEDGE_BASE"
            }
        )

        response_body = AnswerResponseBody.from_retrieve_and_generate_response(bedrock_response).model_dump_json()

        response = ApiGatewayResponse(
            statusCode = 200,
            headers = {"Content-Type": "application/json"},
            body = response_body,
            isBase64Encoded = False
        ).model_dump()

        logger.debug(response)

        return response
        
    
    except ValidationError as ve:
        logger.exception(ve)
        return ApiGatewayResponse(
            statusCode = 400,
            headers = {"Content-Type": "application/json"},
            body = "Bad request",
            isBase64Encoded = False
        ).model_dump()
    
    except Exception as e:
        logger.exception(e)
        return ApiGatewayResponse(
            statusCode = 500,
            headers = {"Content-Type": "application/json"},
            body = "Internal server error",
            isBase64Encoded = False
        ).model_dump()