# app.py
from http.client import NO_CONTENT
from langchain_openai import ChatOpenAI
from langchain_openai.embeddings import OpenAIEmbeddings

from langchain_core.tools import tool
from langchain_core.messages import SystemMessage

from langgraph.prebuilt import ToolNode, tools_condition, InjectedStore
from langgraph.graph import StateGraph, MessagesState, END
from langgraph.graph.state import CompiledStateGraph

from langgraph_checkpoint_dynamodb import (
    DynamoDBSaver,
    DynamoDBConfig,
    DynamoDBTableConfig,
)

from typing_extensions import Annotated
import os
from dotenv import load_dotenv

# local modules (adjust if your paths differ)
from vector_stores import InMemoryStore, BaseVectorStore
from apis import build_llm_client, build_embeddings_client
from web_scrape import fetch_documentation, split_document
from history import show_history_menu

# ---------------- Env ----------------
load_dotenv(override=True)
_ = os.getenv("OPENAI_API_KEY")  # just to ensure it's loaded

# ---------------- Clients & store ----------------
llm: ChatOpenAI = build_llm_client()
embeddings: OpenAIEmbeddings = build_embeddings_client()
vector_store: BaseVectorStore = InMemoryStore(embeddings)

# ---------------- Graph ----------------
def build_graph() -> CompiledStateGraph:
    graph_builder = StateGraph(MessagesState)
    tools_node = ToolNode([retrieve])

    graph_builder.add_node(query_or_respond)
    graph_builder.add_node(tools_node)
    graph_builder.add_node(generate)

    graph_builder.set_entry_point("query_or_respond")
    graph_builder.add_conditional_edges(
        "query_or_respond",
        tools_condition,
        {END: END, "tools": "tools"},
    )
    graph_builder.add_edge("tools", "generate")
    graph_builder.add_edge("generate", END)

    # ---- DynamoDB checkpointer (auto-create PK/SK table) ----
    region = os.getenv("AWS_REGION", "us-east-1")
    table_name = os.getenv("CHECKPOINTS_TABLE", "lmai-checkpoints-v2")  # NEW table name!

    cfg = DynamoDBConfig(
        region_name=region,
        table_config=DynamoDBTableConfig(
            table_name=table_name,
            # uses default PK/SK key names expected by this saver
        ),
    )

    # deploy=True will create the table with PK/SK if missing
    checkpointer = DynamoDBSaver(cfg, deploy=True)

    return graph_builder.compile(checkpointer=checkpointer, store=vector_store)

def _retrieve_core(query: str, vector_store: BaseVectorStore) -> tuple[str, list]:
    """Core retrieval logic that can be tested independently."""
    retrieved_docs = vector_store.similarity_search(query, k=2)
    serialized = "\n\n".join(
        (f"Source: {doc.metadata}\nContent: {doc.page_content}")
        for doc in retrieved_docs
    )
    return serialized, retrieved_docs

@tool(response_format="content_and_artifact")
def retrieve(query: str, vector_store: Annotated[BaseVectorStore, InjectedStore()]):
    """Retrieve information related to a query."""
    return _retrieve_core(query, vector_store)

def generate(state: MessagesState):
    """Generate answer."""
    # Collect the most recent tool messages
    recent_tool_messages = []
    for message in reversed(state["messages"]):
        if message.type == "tool":
            recent_tool_messages.append(message)
        else:
            break
    tool_messages = recent_tool_messages[::-1]

        # Format into prompt
    docs_content = "\n\n".join(doc.content for doc in tool_messages)

    system_message_content = f"""
You are the Les Mills B2B Assistant.

SCOPE
- Only answer questions related to Les Mills' B2B context: clubs/gyms, corporate partners, instructors, distributors, enterprise customers, internal engineering, platform operations, or integrations.
- If the user's intent is ambiguous, assume they're asking about the Les Mills content platform and clarify minimally when essential.

GUARDRAILS
- If a question is not B2B or not supported by the provided context, respond exactly with: “Sorry, I can't assist with that.”
- Do not fabricate undocumented features, SLAs, prices, or roadmaps. If the documents don't cover it, say you don't have that information and (optionally) propose next steps (e.g., contact support, provide IDs/logs).
- Never reveal secrets, access tokens, internal URLs, or non-public architecture. Use placeholders like <API_KEY>, <CLIENT_ID>, <ORG_ID>.
- Follow UK English.

SOURCES & TRUTH
- Treat the provided context as the single source of truth. Prefer its terminology and constraints.
- If information is missing or conflicting, say so plainly and stop.

CODE & ANSWER STYLE
- When giving code:
  - Provide a minimal, runnable example with clear imports and comments.
  - Include environment variable placeholders and note required IAM permissions where relevant.
- When giving steps:
  - Use short, numbered steps.
  - Show key config (endpoints, headers, scopes, roles) explicitly.
- Keep answers concise. Use headings only when they help scanning.

REFUSALS
- Consumer fitness, workout advice, unrelated programming, or non-Les Mills → “Sorry, I can't assist with that.”
- Requests for personal data or internal-only documentation → “Sorry, I can't assist with that.”

CONTEXT (verbatim, may be long):
"{NO_CONTENT}"
""".replace("{DOCS_CONTENT}", docs_content)
    # Filter out messages that are not relevant for the prompt
    # Only include human, system, and AI messages without tool calls    
    conversation_messages = [
        m for m in state["messages"]
        if m.type in ("human", "system") or (m.type == "ai" and not m.tool_calls)
    ]
    prompt = [SystemMessage(system_message_content)] + conversation_messages

    response = llm.invoke(prompt)
    return {"messages": [response]}

def query_or_respond(state: MessagesState):
    """Generate tool call for retrieval or respond."""
    llm_with_tools = llm.bind_tools([retrieve])
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

# ---------------- CLI runner ----------------
def main():
    print("\n================================================================================")
    # Load & index docs into the vector store (dev-only)
    doc = fetch_documentation("https://api.content.lesmills.com/docs/v1/content-portal-api.yaml")
    splits = split_document(doc)
    vector_store.add_documents(splits)

    # Always provide a thread_id (critical for saver!)
    region = os.getenv("AWS_REGION", "us-east-1")
    table = os.getenv("CHECKPOINTS_TABLE", "lmai-checkpoints-langchain")
    thread = os.getenv("DEFAULT_THREAD_ID", "cli-session")

    print(f"[debug] Using thread_id: {thread}  region={region}  table={table}")

    app = build_graph().with_config({"configurable": {"thread_id": thread}})

    while True:
        raw_input_text = input("\nAsk the RAG Demon (or enter 'q' to quit, ':menu' for history): ").strip()
        q = raw_input_text.lower()
        if q == "q":
            break
        elif q == ":menu":
            show_history_menu()
            continue

        for step in app.stream(
            {"messages": [{"role": "user", "content": raw_input_text}]},
            stream_mode="values",
        ):
            step["messages"][-1].pretty_print()

# Build the graph for server usage with a default thread_id
graph = build_graph().with_config(
    {"configurable": {"thread_id": os.getenv("DEFAULT_THREAD_ID", "dev-default")}}
)

if __name__ == "__main__":
    main()
