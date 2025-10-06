import pytest

from mypy_boto3_bedrock_agent_runtime.type_defs import RetrieveAndGenerateResponseTypeDef

from bedrock_impl.bedrock import Bedrock
from bedrock_impl.models import Chunk

from pydantic import AnyUrl
from unittest.mock import MagicMock

def test_parse_bedrock_response(bedrock_response):
    bedrock = Bedrock(client = MagicMock())
    response = bedrock.parse_response(response = bedrock_response)

    assert response.content == "This is the generated answer."
    assert response.session_id == "abc123"

    assert len(response.response_parts) == 2

    first_part = response.response_parts[0]
    assert first_part.text == "Part 1 of the answer"
    assert first_part.references == [
        Chunk(text='Reference 1 text', url=AnyUrl('https://example.com/ref1')),
        Chunk(text='Reference 2 text', url=AnyUrl('https://example.com/ref2')),
    ]

    second_part = response.response_parts[1]
    assert second_part.text == "Part 2 of the answer"
    assert second_part.references == [
        Chunk(text='Reference 3 text', url=AnyUrl('https://example.com/ref3'))
    ]
    
def test_generate_response_calls_bedrock_with_correct_params():
    mock_query = "What is the capital of France?"

    expected_response = {
        "output": {"text": "Paris"},
        "sessionId": "abc123",
        "citations": []
    }

    # Mock the client
    client = MagicMock()
    client.retrieve_and_generate = MagicMock(return_value=expected_response)

    bedrock = Bedrock(client=client)

    # Call the method
    result = bedrock.generate_response(mock_query)

    # Assert the response is returned correctly
    assert result == expected_response

    # Assert the client was called with correct params
    client.retrieve_and_generate.assert_called_once_with(
        input={"text": mock_query},
        retrieveAndGenerateConfiguration = {
            'type': 'KNOWLEDGE_BASE',
            'knowledgeBaseConfiguration': {
                'knowledgeBaseId': 'XBOBJWN1MQ',
                'modelArn': 'anthropic.claude-3-5-sonnet-20240620-v1:0',
                'generationConfiguration': {
                    'guardrailConfiguration': {
                        'guardrailId': '3x3fwig8roag',
                        'guardrailVersion': '3'
                    }
                }
            }
        }
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