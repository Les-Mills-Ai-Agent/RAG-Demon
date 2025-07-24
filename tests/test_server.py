import pytest
from httpx import AsyncClient
from ragdemon.server import api  # your FastAPI app

from fastapi.testclient import TestClient
from starlette.testclient import TestClient as StarletteTestClient  # alternative

@pytest.mark.asyncio
async def test_chat_endpoint_with_valid_message():
    test_messages = [
        {"role": "user", "content": "What kind of content does Les Mills offer?"}
    ]

    async with AsyncClient(base_url="http://testserver") as ac:
        response = await ac.post("http://localhost:8000/api/chat", json={"messages": test_messages})

    assert response.status_code == 200
    json_data = response.json()
    assert "reply" in json_data
    assert isinstance(json_data["reply"], str)
    assert len(json_data["reply"]) > 0


@pytest.mark.asyncio
async def test_chat_endpoint_with_empty_message():
    test_messages = []

    async with AsyncClient(base_url="http://testserver") as ac:
        response = await ac.post("http://localhost:8000/api/chat", json={"messages": test_messages})

    assert response.status_code == 400
    assert response.json()["detail"] == "Message list is empty."

