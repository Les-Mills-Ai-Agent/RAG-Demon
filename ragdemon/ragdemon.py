from langchain_openai import ChatOpenAI
from langchain_openai.embeddings import OpenAIEmbeddings
from langgraph.graph import START, StateGraph, MessagesState, END
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

from splitting import split_document
from vector_stores import InMemoryStore, BaseVectorStore

import json
from datetime import datetime

CHAT_HISTORY_FILE = "chat_data/chat_history.json"

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)
os.getenv("OPENAI_API_KEY")

def build_llm_client() -> ChatOpenAI:
    return ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )

def build_embeddings_client() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(
        model="text-embedding-3-large",
    )

llm: ChatOpenAI = build_llm_client()
embeddings: OpenAIEmbeddings = build_embeddings_client()
vector_store: BaseVectorStore = InMemoryStore(embeddings)

config = {"configurable": {"thread_id": "sseijrfbes"}}

def build_graph() -> StateGraph:
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

    memory = MemorySaver()

    return graph_builder.compile(checkpointer=memory)


@tool(response_format="content_and_artifact")
def retrieve(query: str):
    """Retrieve information related to a query."""
    (retrieved_docs, scores) = zip(*vector_store.similarity_search_with_scores(query, k=2))
    serialized = "\n\n".join(
        (f"Source: {doc.metadata}\nContent: {doc.page_content}")
        for doc in retrieved_docs
    )
    return serialized, retrieved_docs

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

def save_chat(state: MessagesState):
    # Attempt to open the existing chat history file in read mode
    try:
        with open(CHAT_HISTORY_FILE, "r") as f:
            #load the existing chat history from the JSON file
            try:
                history = json.load(f)
            except json.JSONDecodeError:
                # If the file is empty or not valid JSON, initialize an empty history list
                history = []
    except FileNotFoundError:
        #if the file doenst exist yet, initalise and empty history list as shown.
        history = []

    # Append the new chat entry to the history with questions timestamps and responses from the Ai model.
    history.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "question": state["question"],
        "response": state["response"]
    })

    #Write the updated History back to the file in JSON Format, with indentations to make sure it is neat.
    with open(CHAT_HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def show_history():
    try:
        with open(CHAT_HISTORY_FILE, "r") as f:
            try:
                history = json.load(f)
            except json.JSONDecodeError:
                # If the file is empty or not valid JSON, initialize an empty history list
                history = []
    except FileNotFoundError:
        print("No previous chats found.")
        return

    if not history:
        print("No previous chats found.")
        return

    for idx, entry in enumerate(history, start=1):
        print(f"\n#{idx} | {entry['timestamp']}")
        print(f"Q: {entry['question']}")
        print(f"A: {entry['response']}")

def main():

    print("\n================================================================================")

    # Load document
    with open("sample_data/description.md", encoding="utf-8") as f:
        document = f.read()
        
    # Split and store the document in the vector store
    splits = split_document(document)
    vector_store.add_documents(splits)

    app = build_graph()

    while True:
        # Get user input for the question
        question = input("\nAsk the RAG Demon (or enter 'q' to quit): ")
        if question.strip().lower() == "q":
            break

        for step in app.stream(
            {"messages": [{"role": "user", "content": question}]},
            stream_mode="values",
            config=config,
        ):
            step["messages"][-1].pretty_print()


# Test the application
if __name__ == "__main__":
    main()