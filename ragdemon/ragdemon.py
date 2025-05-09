from langchain import hub
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_openai.embeddings import OpenAIEmbeddings
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


class RagDemon:

    llm: ChatOpenAI
    embeddings: OpenAIEmbeddings
    vector_store: InMemoryVectorStore

    prompt: ChatPromptTemplate

    context: List[Document]
    answer: str
    scores: List[float]

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
    
    def retrieve(self, question):
        docs, scores = zip(*self.vector_store.similarity_search_with_score(question))
        self.context = docs
        self.scores = scores
        self.question = question


    def generate(self):
        docs_content = "\n\n".join(doc.page_content for doc in self.context)
        messages = self.prompt.invoke({"question": self.question, "context": docs_content})
        response = self.llm.invoke(messages)
        return response.content
    

    def save_chat(self, question, response):
        # Attempt to open the existing chat history file in read mode
        try: 
            with open(CHAT_HISTORY_FILE, "r") as f:
                #load the existing chatr history from the JSON file
                history = json.load(f)
        except FileNotFoundError:
            #if the file doenst exist yet, initalise and empty history list as shown.
            history = []

        # Append the new chat entry to the history with questions timestamps and responses from the Ai model.
        history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "question": question,
            "response": response
        })

        #Write the updated History back to the file in JSON Format, with indentations to make sure it is neat.
        with open(CHAT_HISTORY_FILE, "w") as f:
            json.dump(history, f, indent=2)

    def show_history(self):
        try:
            with open(CHAT_HISTORY_FILE, "r") as f:
                history - json.load(f)
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
    rag_demon.retrieve(question)
    response = rag_demon.generate()

    # save the interaction to the JSON Chat History file
    rag_demon.save_chat(question, response)

    # Print the results
    seperator = "\n" + "=" * 40 + "\n"
    print("RESPONSE:\n", seperator, response, seperator)
    print("DOCUMENTS:\n", seperator)
    for doc in rag_demon.context:
        print(f"Metadata:\n{doc.metadata}\nContent: {doc.page_content}\nScore: {rag_demon.scores[0]}\n")

# Test the application
if __name__ == "__main__":
    main()
