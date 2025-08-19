import pytest
import httpx
from langchain_impl.src.server import api  # FastAPI app


@pytest.mark.asyncio
async def test_chat_endpoint_with_valid_message():
    payload = {
        "session_id": "test-session-123",
        "messages": [
            {"role": "user", "content": "What is the Les Mills Content Portal?"}
        ],
    }

    transport = httpx.ASGITransport(app=api)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.post("/api/chat", json=payload)

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert isinstance(data.get("reply"), str) and len(data["reply"]) > 0
    assert data.get("session_id") == "test-session-123"


@pytest.mark.asyncio
async def test_chat_endpoint_with_empty_message():
    payload = {
        "session_id": "test-session-456",
        "messages": [],  # triggers your 400 branch
    }

    transport = httpx.ASGITransport(app=api)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.post("/api/chat", json=payload)

    assert resp.status_code == 400, resp.text
    assert resp.json()["detail"] == "messages must be a non-empty list"
