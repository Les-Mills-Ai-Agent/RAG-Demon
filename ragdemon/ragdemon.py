from langchain import hub
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_openai.embeddings import OpenAIEmbeddings
from langgraph.graph import START, StateGraph
from typing_extensions import List, TypedDict

import json
from datetime import datetime

CHAT_HISTORY_FILE = "chat_data/chat_history.json"

from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    MarkdownHeaderTextSplitter,
)

from typing_extensions import List
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)
os.getenv("OPENAI_API_KEY")

class State(TypedDict):
    question: str
    context: List[Document]
    response: str
    scores: List[float]

class RagDemon:

    llm: ChatOpenAI
    embeddings: OpenAIEmbeddings
    vector_store: InMemoryVectorStore

    prompt: ChatPromptTemplate

    graph: StateGraph

    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            max_tokens=None,
        )

        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-large",
        )

        self.vector_store = InMemoryVectorStore(self.embeddings)

        self.prompt = hub.pull("rlm/rag-prompt")

        graph_builder = StateGraph(State).add_sequence([self.retrieve, self.generate, self.save_chat, self.print_response])
        graph_builder.add_edge(START, "retrieve")
        self.graph = graph_builder.compile()

    def split_document(self, document) -> List[Document]:

        headers_to_split_on = [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
            ("####", "Header 4"),
        ]

        md_splitter = MarkdownHeaderTextSplitter(headers_to_split_on)
        md_splits = md_splitter.split_text(document)

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=50,
            separators=[". ", "\n\n", "\n"],
        )

        return text_splitter.split_documents(md_splits)

    def store_splits(self, splits: List[Document]): 
        self.vector_store.add_documents(documents=splits)
    
    def retrieve(self, state: State):
        docs, scores = zip(*self.vector_store.similarity_search_with_score(state["question"]))
        return {
            "context": docs,
            "scores": scores,
        }


    def generate(self, state: State):
        docs_content = "\n\n".join(doc.page_content for doc in state["content"])
        messages = self.prompt.invoke({"question": state["question"], "context": docs_content})
        response = self.llm.invoke(messages)
        return {"response" : response.content}

    def save_chat(self, state: State):
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

    def show_history(self):
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

    def print_response(self, state: State):
        large_seperator = "\n" + "=" * 40 + "\n"
        small_seperator = "\n" + "-" * 40 + "\n"
        print(large_seperator, "RESPONSE", large_seperator, "\n", state["response"])
        print(large_seperator, "CONTEXT:", large_seperator)
        for i, doc in enumerate(state["context"]):
            print(small_seperator, f"DOCUMENT {i + 1}", small_seperator)
            print(f"Metadata:\n\n{doc.metadata}\n\nContent:\n\n{doc.page_content}\n\nScore: {state['scores'][i]}")

def main():
    # Initialize the RAGDemon application
    rag_demon = RagDemon()

    # Load document
    with open("sample_data/description.md", encoding="utf-8") as f:
        document = f.read()
        
    # Split and store the document in the vector store
    splits = rag_demon.split_document(document)
    rag_demon.store_splits(splits)

    # Get user input for the question
    question = input("Ask a question about the document (press enter to continue): ")

    # Retrieve relevant documents and generate an answer
    rag_demon.graph.invoke(
        {
            "question": question
        }
    )

# Test the application
if __name__ == "__main__":
    main()