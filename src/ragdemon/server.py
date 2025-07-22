# server.py
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from ragdemon.app import build_graph

# load env
load_dotenv(override=True)
if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("Set OPENAI_API_KEY in your .env")

# import your RAG graph builder

graph = build_graph()

class ChatRequest(BaseModel):
    messages: list[dict]

api = FastAPI()
api.add_middleware(
  CORSMiddleware,
  allow_origins=["http://localhost:5173"],
  allow_methods=["*"],
  allow_headers=["*"],
)

@api.post("/api/chat")
async def chat(req: ChatRequest):
    try:
        final = None
        for step in graph.stream(
            {"messages": req.messages},
            stream_mode="values",
        ):
            msg = step["messages"][-1]
            if getattr(msg, "type", None) in ("ai", "assistant"):
                final = msg.content
        if final is None:
            raise RuntimeError("No assistant reply")
        return {"reply": final}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:api", host="0.0.0.0", port=8000, reload=True)
