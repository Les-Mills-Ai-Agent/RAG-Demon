from langchain_openai import ChatOpenAI
from langchain_openai.embeddings import OpenAIEmbeddings

from langchain_core.tools import tool
from langchain_core.messages import SystemMessage

from langgraph.prebuilt import ToolNode, tools_condition, InjectedStore
from langgraph.graph import StateGraph, MessagesState, END
from langgraph.graph.state import CompiledStateGraph

from langgraph_checkpoint_dynamodb import DynamoDBSaver




from typing_extensions import Annotated
import boto3

from .vector_stores import InMemoryStore, BaseVectorStore
from .apis import build_llm_client, build_embeddings_client
from .web_scrape import fetch_documentation, split_document
from .history import show_history_menu

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)
os.getenv("OPENAI_API_KEY")


# create dynamodb client
dynamodb_client = boto3.client(
    "dynamodb",
    region_name=os.getenv("AWS_REGION", "us-east-1")
)
# NOTE: DynamoDBSaver below uses a boto3 *resource* (Table), not the client.
# The client is left here intentionally to preserve your original comment/history.

llm: ChatOpenAI = build_llm_client()
embeddings: OpenAIEmbeddings = build_embeddings_client()
vector_store: BaseVectorStore = InMemoryStore(embeddings)

def build_graph() -> CompiledStateGraph:
    graph_builder = StateGraph(MessagesState)
    tools = ToolNode([retrieve])
    
    graph_builder.add_node(query_or_respond)
    graph_builder.add_node(tools)
    graph_builder.add_node(generate)

    graph_builder.set_entry_point("query_or_respond")
    graph_builder.add_conditional_edges(
        "query_or_respond",
        tools_condition,
        {END: END, "tools": "tools"},
    )
    graph_builder.add_edge("tools", "generate")
    graph_builder.add_edge("generate", END)

    # ---- DynamoDB checkpointer (stateless persistence by thread_id) ----
    ddb = boto3.resource(
        "dynamodb",
        region_name=os.getenv("AWS_REGION", "us-east-1")
    )
    table_name = os.getenv("CHECKPOINTS_TABLE", "lmai-checkpoints")
    checkpointer = DynamoDBSaver(ddb.Table(table_name))

    return graph_builder.compile(checkpointer=checkpointer, store=vector_store)

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
            # In server mode, pass config={"configurable":{"thread_id": <session_id>}}
        ):
            step["messages"][-1].pretty_print()

# Build the graph for server usage
graph = build_graph()
# Test the application
if __name__ == "__main__":
    main()
