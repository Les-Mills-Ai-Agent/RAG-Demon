import os
from typing import List, Literal, Optional
from uuid import uuid4
import uvicorn

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ValidationError
from dotenv import load_dotenv
load_dotenv(override=True)

from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    SystemMessage,
    ToolMessage,
    AnyMessage,
)

from langchain_core.runnables import RunnableConfig

# ---- Local config (do NOT import these from app.py) ----
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
CHECKPOINTS_TABLE = os.getenv("CHECKPOINTS_TABLE", "lmai-checkpoints-langchain")

# Import graph + shared components from app.py
from langchain_impl.app import (
    build_graph,
    vector_store,
    sanitize_messages,   # orphan-tool cleaner
)

from langchain_impl.web_scrape import fetch_documentation, split_document


# ---------- Env ----------

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("Set OPENAI_API_KEY in your environment.")

# allow comma-separated CORS origins: "http://localhost:5173,https://app.example.com"
_frontend_origins = os.getenv(
    "FRONTEND_ORIGINS",
    os.getenv("FRONTEND_ORIGIN", "http://localhost:5173"),
)
ALLOWED_ORIGINS = [o.strip() for o in _frontend_origins.split(",") if o.strip()]


# ---------- (DEV) Index docs at import ----------
# For production, pre-index in your vector DB instead of doing this at startup.
document = fetch_documentation(
    "https://api.content.lesmills.com/docs/v1/content-portal-api.yaml"
)
splits = split_document(document)
vector_store.add_documents(splits)


# ---------- Graph ----------
graph = build_graph()  # compiled with DynamoDB checkpointer + shared store


# We don’t use LangChain’s message objects here.
# Instead, we make our own Pydantic model so:
# 1. The API uses plain JSON (easy for frontend).
# 2. FastAPI can check the data is valid.
# 3. We aren’t tied to LangChain’s internal code.

# ---------- Schemas ----------
class Message(BaseModel):
    role: Literal["user", "assistant", "system", "tool"]
    content: str = Field(min_length=1)
    # Optional fields if you ever pass tool results from the client
    tool_call_id: Optional[str] = None
    name: Optional[str] = None


class ChatRequest(BaseModel):
    # If client omits session_id, we create a fresh one (stateless by default)
    session_id: Optional[str] = None
    messages: List[Message]


# ---------- Helpers ----------
def to_lc_message(m: Message) -> AnyMessage:
    if m.role == "user":
        return HumanMessage(content=m.content)
    if m.role == "assistant":
        return AIMessage(content=m.content)
    if m.role == "system":
        return SystemMessage(content=m.content)
    if m.role == "tool":
        # Only meaningful if client ever sends tool outputs; harmless otherwise
        return ToolMessage(content=m.content, tool_call_id=m.tool_call_id or "client_tool")
    raise ValueError(f"Unsupported role: {m.role}")


def new_thread_id(prefix: str = "web") -> str:
    return f"{prefix}-{uuid4()}"


# ---------- FastAPI ----------
api = FastAPI(title="Les Mills RAG API")

api.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


@api.get("/health")
async def health():
    return {"status": "ok"}


@api.post("/api/chat")
async def chat(req: ChatRequest):
    try:
        if not req.messages:
            raise HTTPException(status_code=400, detail="messages must be a non-empty list")

        # Fresh stateless session unless the client explicitly wants continuity
        session_id = req.session_id or new_thread_id("web")
        config = RunnableConfig({"configurable": {"thread_id": session_id}})

        # Convert inbound payload into LC messages and clean stray tool messages
        lc_messages = [to_lc_message(m) for m in req.messages]
        cleaned = sanitize_messages(lc_messages)

        # Prepend a routing nudge so first turn reliably calls `retrieve`
        routing_nudge = SystemMessage(
            "Routing: For questions about Les Mills, the Content Portal, APIs, integrations, "
            "platform, engineering, or operations, you MUST call the `retrieve` tool first. "
            "Only skip tools if clearly unrelated."
        )
        messages_for_graph = [routing_nudge] + cleaned

        # Helpful logs
        print(f"[server] thread_id={session_id}  region={AWS_REGION}  table={CHECKPOINTS_TABLE}")
        for i, m in enumerate(messages_for_graph):
            role = getattr(m, "type", None)
            preview = (getattr(m, "content", "") or "")[:120].replace("\n", " ")
            print(f"[server] in[{i}] {role}: {preview!r}")

        assistant_response = None

        # Stream using the full message list; checkpointer will hydrate prior state (if any)
        for step in graph.stream(
            {"messages": messages_for_graph},
            stream_mode="values",
            config=config,
        ):
            last = step["messages"][-1]
            if isinstance(last, AIMessage) and getattr(last, "tool_calls", None):
                print(f"[server] tool_calls: {len(last.tool_calls)}")
            if getattr(last, "type", None) in ("ai", "assistant"):
                assistant_response = last.content

        if not assistant_response:
            raise HTTPException(status_code=500, detail="No assistant message generated.")

        return {"reply": assistant_response, "session_id": session_id}

    except ValidationError as ve:
        raise HTTPException(status_code=400, detail=str(ve)) from ve
    except HTTPException:
        raise
    except Exception as e:
        print(f"[server.chat] {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred. Please try again later.")


# Dev server entry point
if __name__ == "__main__":
    uvicorn.run("server:api", host="0.0.0.0", port=8000, reload=True)
