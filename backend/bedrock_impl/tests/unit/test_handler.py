import pytest
from mypy_boto3_bedrock_agent_runtime.type_defs import RetrieveAndGenerateResponseTypeDef, RetrieveAndGenerateConfigurationTypeDef
from bedrock_impl.src.handler import parse_bedrock_response, generate_response
from unittest.mock import MagicMock
import json

def test_parse_bedrock_response(bedrock_response):

    response_json = parse_bedrock_response(bedrock_response)
    response = json.loads(response_json)

    assert response["answer"] == "This is the generated answer."
    assert response["session_id"] == "abc123"

    assert len(response["responseParts"]) == 2

    first_part = response["responseParts"][0]
    assert first_part["text"] == "Part 1 of the answer"
    assert first_part["references"] == [
        {
            "text": "Reference 1 text",
            "url": "https://example.com/ref1"
        },
        {
            "text": "Reference 2 text",
            "url": "https://example.com/ref2"
        }
    ]

    second_part = response["responseParts"][1]
    assert second_part["text"] == "Part 2 of the answer"
    assert second_part["references"] == [
        {
            "text": "Reference 3 text",
            "url": "https://example.com/ref3"
        }
    ]
    
def test_generate_response_calls_bedrock_with_correct_params():

    mock_client = MagicMock()
    mock_config = RetrieveAndGenerateConfigurationTypeDef(
    type = "KNOWLEDGE_BASE",
    knowledgeBaseConfiguration = {
        "knowledgeBaseId" : "kb123",
        "modelArn": "provider.model:0"
    }
)

    mock_query = "What is the capital of France?"

    expected_response = {
        "output": {"text": "Paris"},
        "sessionId": "abc123",
        "citations": []
    }

    mock_client.retrieve_and_generate.return_value = expected_response

    result = generate_response(mock_query, mock_client, mock_config)

    assert result == expected_response

    mock_client.retrieve_and_generate.assert_called_once_with(
        input={"text": mock_query},
        retrieveAndGenerateConfiguration=mock_config
    )

@pytest.fixture
def bedrock_response():
    return RetrieveAndGenerateResponseTypeDef({
        "output": {
            "text": "This is the generated answer."
        },
        "sessionId": "abc123",
        "guardrailAction": "NONE",
        "ResponseMetadata": {
            "RequestId": "12345",
            "HTTPStatusCode": 200,
            "HTTPHeaders": {
                
            },
            "HostId": "12345",
            "RetryAttempts": 0
        },
        "citations": [
            {
                "generatedResponsePart": {
                    "textResponsePart": {
                        "text": "Part 1 of the answer"
                    }
                },
                "retrievedReferences": [
                    {
                        "content": {"text": "Reference 1 text"},
                        "location": {
                            "type": "WEB",
                            "webLocation": {"url": "https://example.com/ref1"}
                        }
                    },
                    {
                        "content": {"text": "Reference 2 text"},
                        "location": {
                            "type": "WEB",
                            "webLocation": {"url": "https://example.com/ref2"}
                        }
                    }
                ]
            },
            {
                "generatedResponsePart": {
                    "textResponsePart": {
                        "text": "Part 2 of the answer"
                    }
                },
                "retrievedReferences": [
                    {
                        "content": {"text": "Reference 3 text"},
                        "location": {
                            "type": "WEB",
                            "webLocation": {"url": "https://example.com/ref3"}
                        }
                    }
                ]
            }
        ]
    })