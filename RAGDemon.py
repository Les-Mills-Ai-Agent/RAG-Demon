from langchain.chat_models import init_chat_model
from langchain_community.vectorstores.faiss import FAISS
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.vectorstores import InMemoryVectorStore
from langchain import hub
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter
from langchain_core.documents.base import Document
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import START, StateGraph
from typing_extensions import List, TypedDict
import bs4
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)
os.getenv('OPENAI_API_KEY')

def init():
    llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    max_tokens=None,)

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-large",
    )

    vector_store = InMemoryVectorStore(embeddings)

    return llm, embeddings, vector_store

def split_document(document):
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

    all_splits = text_splitter.split_documents(md_splits)

    return all_splits

llm, embeddings, vector_store = init()

# Load document
with open("docs/description.md", "r", encoding="utf-8") as f:
    document = f.read()



splits = split_document(document)

# Add documents to vector store
vector_store.add_documents(documents=splits)

# Define prompt for question-answering
prompt = hub.pull("rlm/rag-prompt")


# Define state for application
class State(TypedDict):
    question: str
    context: List[Document]
    answer: str
    scores: List[float]


# Define application steps
def retrieve(state: State):
    docs, scores = zip(*vector_store.similarity_search_with_score(state["question"]))
    return {"context": docs, "scores": scores}

def generate(state: State):
    docs_content = "\n\n".join(doc.page_content for doc in state["context"])
    messages = prompt.invoke({"question": state["question"], "context": docs_content})
    response = llm.invoke(messages)
    return {"answer": response.content}


# Compile application and test
graph_builder = StateGraph(State).add_sequence([retrieve, generate])
graph_builder.add_edge(START, "retrieve")
graph = graph_builder.compile()

# Test the application
question = input("Ask a question about the document (press enter to continue): ")

response = graph.invoke({"question": question})
print("DOCUMENTS:")
print("=====================================")
for i in range(len(response["context"])):
  doc = response["context"][i]
  print(f'SCORE: {response["scores"][i]}')
  print(f'METADATA: {doc.metadata}\nCONTENT: {doc.page_content}\n\n')
  print("=====================================")

print('RESPONSE:')
print("=====================================")
print(response["answer"])

print("\n=====================================")
print("REFERENCES:")
print("=====================================")
for i in range(len(response["context"])):
  doc = response["context"][i]
  print(" - ".join(doc.metadata.values()))