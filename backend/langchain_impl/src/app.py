from http.client import NO_CONTENT
from langchain_openai import ChatOpenAI
from langchain_openai.embeddings import OpenAIEmbeddings

from langchain_core.tools import tool
from langchain_core.messages import SystemMessage

from langgraph.prebuilt import ToolNode, tools_condition, InjectedStore
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, MessagesState, END
from langgraph.graph.state import CompiledStateGraph

from typing_extensions import Annotated

from .vector_stores import InMemoryStore, BaseVectorStore
from .apis import build_llm_client, build_embeddings_client
from .web_scrape import fetch_documentation, split_document
from .history import save_chat
from .history import show_history_menu

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)
os.getenv("OPENAI_API_KEY")

llm: ChatOpenAI = build_llm_client()
embeddings: OpenAIEmbeddings = build_embeddings_client()
vector_store: BaseVectorStore = InMemoryStore(embeddings)

config = {"configurable": {"thread_id": "bomboclaat_thread"}}

def build_graph() -> CompiledStateGraph:
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

    system_message_content = f"""
You are the Les Mills B2B Assistant.

SCOPE
- Only answer questions related to Les Mills' B2B context: clubs/gyms, corporate partners, instructors, distributors, enterprise customers, internal engineering, platform operations, or integrations.
- Provide hands-on technical help for implementation and integrations (e.g., React/Node/TypeScript, Python, AWS Lambda/API Gateway/CloudFront/S3/Cognito, webhooks, OAuth, REST/GraphQL, SDK usage).
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
  - Use modern defaults (e.g., AWS SDK v3, async/await, fetch or axios). Avoid deprecated APIs.
- When giving steps:
  - Use short, numbered steps.
  - Show key config (endpoints, headers, scopes, roles) explicitly.
- Keep answers concise. Use headings only when they help scanning.

REFUSALS
- Consumer fitness, workout advice, unrelated programming, or non-Les Mills topics → “Sorry, I can't assist with that.”
- Requests for personal data or internal-only documentation → “Sorry, I can't assist with that.”

CONTEXT (verbatim, may be long):
"{NO_CONTENT}"
""".replace("{DOCS_CONTENT}", docs_content)
    # Filter out messages that are not relevant for the prompt
    # Only include human, system, and AI messages without tool calls    
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

# Step 1: Generate an AIMessage that may include a tool-call to be sent.
def query_or_respond(state: MessagesState):
    """Generate tool call for retrieval or respond."""
    llm_with_tools = llm.bind_tools([retrieve])
    response = llm_with_tools.invoke(state["messages"])
    # MessagesState appends messages to state instead of overwriting
    return {"messages": [response]}

def main():
    print("\n================================================================================")

    # Load and index documentation into the vector store
    document = fetch_documentation("https://api.content.lesmills.com/docs/v1/content-portal-api.yaml")
    splits = split_document(document)
    vector_store.add_documents(splits)

    app = build_graph()

    while True:
        # Prompt user for input or special command
        raw_input = input("\nAsk the RAG Demon (or enter 'q' to quit, ':menu' for history): ").strip()
        question = raw_input.lower()
        # Handle special commands

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



# Build the graph for server usage
graph = build_graph()
# Test the application
if __name__ == "__main__":
    main()