from langchain_openai import ChatOpenAI
from langchain_openai.embeddings import OpenAIEmbeddings

from langchain_core.tools import tool
from langchain_core.messages import SystemMessage

from langgraph.prebuilt import ToolNode, tools_condition, InjectedStore
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, MessagesState, END

from typing_extensions import Annotated

from ragdemon.vector_stores import InMemoryStore, BaseVectorStore
from ragdemon.apis import build_llm_client, build_embeddings_client
from ragdemon.web_scrape import fetch_documentation, split_document
from ragdemon.history import save_chat
from ragdemon.history import show_history_menu

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)
os.getenv("OPENAI_API_KEY")


llm: ChatOpenAI = build_llm_client()
embeddings: OpenAIEmbeddings = build_embeddings_client()
vector_store: BaseVectorStore = InMemoryStore(embeddings)

config = {"configurable": {"thread_id": "bomboclaat_thread"}}


# ── MOVE THESE UP ────────────────────────────────────────────────────────────────

def _retrieve_core(query: str, vector_store) -> tuple[str, list]:
    """Core retrieval logic that can be tested independently."""
    retrieved_docs = vector_store.similarity_search(query, k=2)
    serialized = "\n\n".join(
        (f"Source: {doc.metadata}\nContent: {doc.page_content}")
        for doc in retrieved_docs
    )
    return serialized, retrieved_docs

@tool(response_format="content_and_artifact")
def retrieve(query: str, vector_store: Annotated[any, InjectedStore()]):
    """Retrieve information related to a query."""
    return _retrieve_core(query, vector_store)

def generate(state: MessagesState):
    """Generate answer."""
    # Get generated ToolMessages
    recent_tool_messages = []
    for message in reversed(state["messages"]):
        if message.type == "tool":
            recent_tool_messages.append(message)
        else:
            break
    tool_messages = recent_tool_messages[::-1]

    # Format into prompt
    docs_content = "\n\n".join(doc.content for doc in tool_messages)
    system_message_content = (
        "You are a helpful customer service assistant."
        "Your task is to answer the user's question based on the provided context."
        "If the question is ambiguous, assume the user is asking about the Les Mills content platform."
        "If the question is not related to the context, respond with 'I don't know'."
        "\n\n"
        f"{docs_content}"
    )
    conversation_messages = [
        message
        for message in state["messages"]
        if message.type in ("human", "system")
        or (message.type == "ai" and not message.tool_calls)
    ]
    prompt = [SystemMessage(system_message_content)] + conversation_messages

    # Run
    response = llm.invoke(prompt)
    return {"messages": [response]}

def query_or_respond(state: MessagesState):
    """Generate tool call for retrieval or respond."""
    llm_with_tools = llm.bind_tools([retrieve])
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

# ── END MOVE ─────────────────────────────────────────────────────────────────────


def build_graph() -> StateGraph:
    graph_builder = StateGraph(MessagesState)
    tools = ToolNode([retrieve])
    
    graph_builder.add_node(query_or_respond)
    graph_builder.add_node(tools)
    graph_builder.add_node(generate)
    graph_builder.add_node(save_chat)

    graph_builder.set_entry_point("query_or_respond")
    graph_builder.add_conditional_edges(
        "query_or_respond",
        tools_condition,
        {END: END, "tools": "tools"},
    )
    graph_builder.add_edge("tools", "generate")
    graph_builder.add_edge("generate", "save_chat")
    graph_builder.add_edge("save_chat", END)

    memory = MemorySaver()
    return graph_builder.compile(checkpointer=memory, store=vector_store)


# Build the graph once at import time
graph = build_graph()


# FastAPI setup

class ChatRequest(BaseModel):
    messages: list[dict]

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
        for step in graph.stream({"messages": req.messages}, stream_mode="values"):
            msg = step["messages"][-1]
            if getattr(msg, "type", None) in ("ai", "assistant"):
                reply = msg.content
        if reply is None:
            raise RuntimeError("No assistant reply produced")
        return {"reply": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def main():
    print("\n" + "="*80)

    # Load and index documentation into the vector store
    document = fetch_documentation(
        "https://api.content.lesmills.com/docs/v1/content-portal-api.yaml"
    )
    splits = split_document(document)
    vector_store.add_documents(splits)

    app = build_graph()

    while True:
        # Prompt user for input or special command
        raw_input = input(
            "\nAsk the RAG Demon (or enter 'q' to quit, ':menu' for history): "
        ).strip()
        question = raw_input.lower()

        if question == "q":
            break
        elif question == ":menu":
            show_history_menu()
            continue  # return to main prompt after menu

        # Stream response from the AI
        for step in app.stream(
            {"messages": [{"role": "user", "content": raw_input}]},
            stream_mode="values",
            config=config,
        ):
            step["messages"][-1].pretty_print()


if __name__ == "__main__":
    main()
