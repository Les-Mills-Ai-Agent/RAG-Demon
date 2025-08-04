from typing import Any
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools import Logger
from model import QuestionRequest, ErrorResponse, AnswerResponse
from pydantic import ValidationError
import boto3
from mypy_boto3_bedrock_agent_runtime.type_defs import RetrieveAndGenerateResponseTypeDef

logger = Logger(service="my-service", level="DEBUG")


def bedrock_handler(event: dict[str, Any], context: LambdaContext) -> str:
    try:
        client = boto3.client('bedrock-agent-runtime')

        request = QuestionRequest.model_validate_json(event["body"])

        raw_response: RetrieveAndGenerateResponseTypeDef = client.retrieve_and_generate(
            input={"text": request.query},
            retrieveAndGenerateConfiguration={
                "knowledgeBaseConfiguration": {
                    "knowledgeBaseId": "XBOBJWN1MQ",
                    "modelArn": "anthropic.claude-3-5-sonnet-20240620-v1:0"
                },
                "type": "KNOWLEDGE_BASE"
            }
        )

        return AnswerResponse.from_retrieve_and_generate_response(raw_response).model_dump_json()
    
    except ValidationError as ve:
        logger.exception(ve)
        return ErrorResponse(
            message = "Bad request",
            code = 400
        ).model_dump_json()
    
    except Exception as e:
        logger.exception(e)
        return ErrorResponse(
            message = "Internal server error",
            code = 500
        ).model_dump_json()