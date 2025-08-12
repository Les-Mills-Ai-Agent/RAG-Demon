import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from .app import build_graph, vector_store, config
from .web_scrape import fetch_documentation, split_document

# Load environment variables
load_dotenv(override=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")

if not OPENAI_API_KEY:
    raise RuntimeError("Set OPENAI_API_KEY in your .env")

# Ensure chat history folder exists
os.makedirs("chat_data", exist_ok=True)

# Load and index documentation
document = fetch_documentation("https://api.content.lesmills.com/docs/v1/content-portal-api.yaml")
splits = split_document(document)
vector_store.add_documents(splits)

# Build the LangGraph pipeline
graph = build_graph()

# Pydantic model for incoming requests
class ChatRequest(BaseModel):
    messages: list[dict]

# Create FastAPI app
api = FastAPI(title="Les Mills RAG API")

# Add CORS middleware using env variable
api.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_methods=["*"],
    allow_headers=["*"],
)

@api.post("/api/chat")
async def chat(req: ChatRequest):
    try:
        if not req.messages or not isinstance(req.messages, list):
            raise HTTPException(status_code=400, detail="Message list is empty or invalid.")

        # Just extract the latest message
        latest_msg = req.messages[-1]

        # Start streaming into LangGraph with only the new message
        assistant_response = None
        for step in graph.stream(
            {"messages": [latest_msg]},
            stream_mode="values",
            config=config
        ):
            msg = step["messages"][-1]
            if getattr(msg, "type", None) in ("ai", "assistant"):
                assistant_response = msg.content

        if assistant_response is None:
            raise RuntimeError("No assistant message generated — check input or node config.")

        return {"reply": assistant_response}

    except HTTPException:
        raise
    except Exception as e:
        print(f"Internal Server Error: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred. Please try again later.")




# Dev server entry point
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:api", host="0.0.0.0", port=8000, reload=True)
