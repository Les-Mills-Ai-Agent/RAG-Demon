import os
from typing import List, Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ValidationError
from dotenv import load_dotenv

from app import build_graph, vector_store
from web_scrape import fetch_documentation, split_document


# ---------- Env ----------
load_dotenv(override=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("Set OPENAI_API_KEY in your environment.")

# allow comma-separated CORS origins: "http://localhost:5173,https://app.example.com"
_frontend_origins = os.getenv("FRONTEND_ORIGINS", os.getenv("FRONTEND_ORIGIN", "http://localhost:5173"))
ALLOWED_ORIGINS = [o.strip() for o in _frontend_origins.split(",") if o.strip()]

# ---------- (DEV) Index docs at import ----------
# For production Lambdas, pre-index in your vector DB instead of doing this at startup.
document = fetch_documentation("https://api.content.lesmills.com/docs/v1/content-portal-api.yaml")
splits = split_document(document)
vector_store.add_documents(splits)

# ---------- Graph ----------
graph = build_graph()  # compiled with DynamoDB checkpointer

# ---------- Schemas ----------
class Message(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str = Field(min_length=1)

class ChatRequest(BaseModel):
    session_id: str = Field(min_length=1)   # becomes thread_id
    messages: List[Message]

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

        # Use the latest message; LangGraph + DynamoDB resumes full state by thread_id
        latest_msg = req.messages[-1].model_dump()

        # REQUIRED for stateless persistence
        config = {"configurable": {"thread_id": req.session_id}}

        assistant_response = None
        for step in graph.stream(
            {"messages": [latest_msg]},
            stream_mode="values",
            # If you compile WITHOUT a default store in app.py, uncomment:
            # store=vector_store,
            config=config,
        ):
            msg = step["messages"][-1]
            if getattr(msg, "type", None) in ("ai", "assistant"):
                assistant_response = msg.content

        if not assistant_response:
            raise HTTPException(status_code=500, detail="No assistant message generated.")

        return {"reply": assistant_response, "session_id": req.session_id}

    except ValidationError as ve:
        # Pydantic field-level errors
        raise HTTPException(status_code=400, detail=str(ve)) from ve
    except HTTPException:
        raise
    except Exception as e:
        # Keep stack traces in logs; return generic error to client
        print(f"[server.chat] {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred. Please try again later.")

# Dev server entry point
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:api", host="0.0.0.0", port=8000, reload=True)
