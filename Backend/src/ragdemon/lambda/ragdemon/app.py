import json
from typing import Any
from aws_lambda_powertools.utilities.typing import LambdaContext
import boto3


def bedrock_handler(event: dict[str, Any], context: LambdaContext) -> dict:
    try:
        client = boto3.client('bedrock-agent-runtime')

        body = json.loads(event["body"])

        client.retrieve_and_generate(
            input=body["query"]
        )

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "hello world",
            }),
        }
    
    except ValueError:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "error": "Invalid request body",
            }),
        }
    
    except (KeyError, json.JSONDecodeError):
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Invalid request body"})
            }


def langchain_handler(event: dict[str, Any], context: LambdaContext) -> dict:
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "hello world",
        }),
    }
