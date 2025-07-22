import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# load env
load_dotenv(override=True)
if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("Set OPENAI_API_KEY in your .env")

# import your RAG graph, shared vector store, and config
from ragdemon.app import build_graph, vector_store, config
from ragdemon.web_scrape import fetch_documentation, split_document

# ensure chat history directory exists
import os as _os
_os.makedirs('chat_data', exist_ok=True)

# index documentation before building the graph
document = fetch_documentation(
    "https://api.content.lesmills.com/docs/v1/content-portal-api.yaml"
)
splits = split_document(document)
vector_store.add_documents(splits)

# compile the state graph with indexed documents
graph = build_graph()

# define request schema
class ChatRequest(BaseModel):
    messages: list[dict]

# spin up FastAPI
api = FastAPI(title="Les Mills RAG API")
api.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@api.post("/api/chat")
async def chat(req: ChatRequest):
    try:
        reply = None
        for step in graph.stream({"messages": req.messages}, stream_mode="values", config=config):
            msg = step["messages"][-1]
            if getattr(msg, "type", None) in ("ai", "assistant"):
                reply = msg.content
        if reply is None:
            raise RuntimeError("No assistant reply produced")
        return {"reply": reply}
    except Exception as e:
        import traceback; traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:api", host="0.0.0.0", port=8000, reload=True)
