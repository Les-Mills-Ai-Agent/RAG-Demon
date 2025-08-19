from typing import Any
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools import Logger
from bedrock_impl.src.model import QuestionRequest, AnswerResponseBody
from pydantic import ValidationError
import boto3
from mypy_boto3_bedrock_agent_runtime.type_defs import RetrieveAndGenerateResponseTypeDef, RetrieveAndGenerateConfigurationTypeDef
from mypy_boto3_bedrock_agent_runtime import AgentsforBedrockRuntimeClient


def get_bedrock_client() -> AgentsforBedrockRuntimeClient:
    return boto3.client("bedrock-agent-runtime")


def get_bedrock_config() -> RetrieveAndGenerateConfigurationTypeDef:
    return RetrieveAndGenerateConfigurationTypeDef(
        type="KNOWLEDGE_BASE",
        knowledgeBaseConfiguration={
            "knowledgeBaseId": "XBOBJWN1MQ",
            "modelArn": "anthropic.claude-3-5-sonnet-20240620-v1:0",
            "generationConfiguration": {
                "guardrailConfiguration": {
                    "guardrailId": "3x3fwig8roag",
                    "guardrailVersion": "1",
                }
            }
        }
    )


def bedrock_handler(event: dict[str, Any], context: LambdaContext) -> dict[str, Any]:
    """
    AWS Lambda handler for Bedrock RAG queries.
    """
    try:
        request = parse_request(event["body"])
        bedrock_client = get_bedrock_client()
        bedrock_config = get_bedrock_config()

        bedrock_response = generate_response(request.query, bedrock_client, bedrock_config)
        response_body = parse_bedrock_response(bedrock_response)

        return {
            "statusCode": 200,
            "body": response_body,
        }

    except ValidationError as ve:
        return {"statusCode": 400, "body": "Bad request"}

    except Exception as e:
        return {"statusCode": 500, "body": "Internal server error"}


def parse_request(body: str) -> QuestionRequest:
    """
    Parse and validate the incoming JSON request body into a QuestionRequest.
    """
    return QuestionRequest.model_validate_json(body)


def generate_response(
    query: str,
    bedrock_client: AgentsforBedrockRuntimeClient,
    bedrock_config: RetrieveAndGenerateConfigurationTypeDef,
) -> RetrieveAndGenerateResponseTypeDef:
    """
    Send the query to Bedrock and get the response.
    """
    return bedrock_client.retrieve_and_generate(
        input={"text": query},
        retrieveAndGenerateConfiguration=bedrock_config,
    )


def parse_bedrock_response(response: RetrieveAndGenerateResponseTypeDef) -> str:
    """
    Parse the Bedrock response and return a JSON string of AnswerResponseBody.
    """
    output = response.get("output", {}).get("text")
    session_id = response.get("sessionId")
    citations = response.get("citations", [])

    extracted_parts = []

    for citation in citations:
        generated_response_part = citation.get("generatedResponsePart")
        part_text = None
        if generated_response_part:
            text_response_part = generated_response_part.get("textResponsePart")
            if text_response_part:
                part_text = text_response_part.get("text")

        refs = citation.get("retrievedReferences", [])
        simplified_refs = [
            {
                "text": ref.get("content", {}).get("text"),
                "url": ref.get("location", {}).get("webLocation", {}).get("url"),
            }
            for ref in refs
            if ref.get("location", {}).get("type") == "WEB"
        ]

        extracted_parts.append({
            "text": part_text,
            "references": simplified_refs,
        })

    return AnswerResponseBody(
        answer=output,
        responseParts=extracted_parts,
        session_id=session_id
    ).model_dump_json()