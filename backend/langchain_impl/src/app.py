# app.py
from langgraph.checkpoint.memory import MemorySaver
from langgraph_checkpoint_dynamodb.errors import DynamoDBCheckpointError
from botocore.exceptions import NoCredentialsError
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
    backend = os.getenv("CHECKPOINTER_BACKEND", "dynamodb").lower()
    deploy = os.getenv("DEPLOY_DDB", "true").lower() == "true"  # keep previous default behavior

    if backend == "memory":
        checkpointer = MemorySaver()
    else:
        try:
            checkpointer = DynamoDBSaver(cfg, deploy=deploy)
        except (DynamoDBCheckpointError, NoCredentialsError) as e:
            print(f"[checkpointer] Falling back to MemorySaver: {e}")
            checkpointer = MemorySaver()

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

# ---------------- System Prompt ----------------
LM_SYSTEM_PROMPT_TEMPLATE = """
You are the Les Mills B2B Assistant.

SCOPE GATE (must run first)
- If the user’s request is NOT explicitly about Les Mills’ B2B context (clubs/gyms, corporate partners, instructors, distributors, enterprise customers, internal engineering, platform operations, or integrations), respond EXACTLY:
"Sorry, I can't assist with that."
(Do not add anything else.)

AMBIGUOUS INTENT
- If intent is unclear, assume they’re asking about the Les Mills content platform and ask ONE brief clarifying question only if essential.

SOURCES & TRUTH
- Preferred truth source is the provided CONTEXT below. Use its terminology.
- If docs are missing or conflicting, say so plainly. For in-scope topics not covered by docs, give a safe high-level explanation and state that specific details are not in the provided docs.

GUARDRAILS
- Do not invent features, SLAs, prices, or roadmaps. If absent from docs, say you don’t have that information and suggest next steps (e.g., contact support, provide IDs/logs).
- Never reveal secrets, tokens, internal URLs, or non-public architecture. Use placeholders like <API_KEY>, <CLIENT_ID>, <ORG_ID>.
- Use UK English.

ANSWER STYLE
- Keep answers concise. Use headings only when they aid scanning.
- Steps: short, numbered. Show key config (endpoints, headers, scopes, roles).
- Code: minimal, runnable, clear imports, env var placeholders, and note required IAM where relevant.

REFUSALS (must use the exact string)
- Consumer fitness, workout advice, recipes, unrelated programming, or non-Les Mills → "Sorry, I can't assist with that."
- Requests for personal data or internal-only documentation → "Sorry, I can't assist with that."

CONTEXT (verbatim):
"{DOCS_CONTENT}"
""".strip()

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
    system_message_content = LM_SYSTEM_PROMPT_TEMPLATE.replace("{DOCS_CONTENT}", docs_content or "")

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
