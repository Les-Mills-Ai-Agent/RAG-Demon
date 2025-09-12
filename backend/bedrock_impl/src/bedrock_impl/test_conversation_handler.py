import json
from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from aws_lambda_powertools.utilities.typing import LambdaContext

from handler import conversation_handler 

context = LambdaContext()


def test_messages(session_id: str):
    """Test /messages/{session_id} locally"""
    mock_event_dict = {
        "httpMethod": "GET",
        "path": f"/rag/bedrock/messages/{session_id}",
        "pathParameters": {"session_id": session_id},
        "headers": {},
        "body": None,
        "requestContext": {"authorizer": {"claims": {"sub": "dummy"}}},
    }
    event = APIGatewayProxyEvent(mock_event_dict)
    response = conversation_handler(event, context)
    print(f"\n--- Messages for session {session_id} ---")
    print("Status code:", response["statusCode"])
    print("Body:", json.dumps(json.loads(response["body"]), indent=2))


def test_conversations(user_id: str):
    """Test /conversations/{user_id} locally"""
    mock_event_dict = {
        "httpMethod": "GET",
        "path": f"/rag/bedrock/conversations/{user_id}",
        "pathParameters": {"user_id": user_id},
        "headers": {},
        "body": None,
        "requestContext": {"authorizer": {"claims": {"sub": user_id}}},
    }
    event = APIGatewayProxyEvent(mock_event_dict)
    response = conversation_handler(event, context)
    print(f"\n--- Conversations for user {user_id} ---")
    print("Status code:", response["statusCode"])
    print("Body:", json.dumps(json.loads(response["body"]), indent=2))


if __name__ == "__main__":
    test_user_id = "4418c4e8-4041-7057-a19a-f1def33de47a"
    test_session_id = "a9927d12-d8a4-4f2c-94fa-ef4dbe102af7"

    test_conversations(test_user_id)
    test_messages(test_session_id)
