from langchain import hub
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_community.document_loaders import WebBaseLoader
import yaml

from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    MarkdownHeaderTextSplitter,
    RecursiveJsonSplitter
)

from typing_extensions import List
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)
os.getenv("OPENAI_API_KEY")
os.getenv("USER_AGENT")


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
        
    def fetch_documentation(self, url):
        loader = WebBaseLoader(url)
        doc_list = loader.load()
        
        document_str = doc_list[0].page_content
        parsed_doc = yaml.safe_load(document_str)

        return [parsed_doc]
    
    def extract_markdown(self, obj):
        md_sections = []
        
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, str) and any(token in value for token in ['#', '*', '`']):
                    md_sections.append(value)
                elif isinstance(value, (dict, list)):
                    md_sections.extend(self.extract_markdown(value))
                    
        elif isinstance(obj, list):
            for item in obj:
                md_sections.extend(self.extract_markdown(item))
                
        return md_sections

    def split_document(self, document) -> List[Document]:

        # Create JSON splits
        json_splitter = RecursiveJsonSplitter(max_chunk_size=1000)
        json_docs = json_splitter.create_documents(document)
        
        # Retrieve nested Markdown snippets
        markdown_strings = self.extract_markdown(document)
        combined_markdown = "\n\n".join(markdown_strings)

        # Create Markdown splits
        headers_to_split_on = [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
            ("####", "Header 4"),
        ]

        md_splitter = MarkdownHeaderTextSplitter(headers_to_split_on)
        md_splits = md_splitter.split_text(combined_markdown)

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=50,
            separators=[". ", "\n\n", "\n"],
        )

        md_docs = text_splitter.split_documents(md_splits)

        # Combine and return both JSON and Markdown splits
        return json_docs + md_docs

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

def main():
    # Initialize the RAGDemon application
    rag_demon = RagDemon()

    # Load document by scraping documentation online
    document = rag_demon.fetch_documentation("https://api.content.lesmills.com/docs/v1/content-portal-api.yaml")

    # Split and store the document in the vector store
    splits = rag_demon.split_document(document)
    rag_demon.store_splits(splits)

    # Get user input for the question
    question = input("Ask a question about the document (press enter to continue): ")

    # Retrieve relevant documents and generate an answer
    rag_demon.retrieve(question)
    response = rag_demon.generate()

    # Print the results
    seperator = "\n" + "=" * 40 + "\n"
    print("RESPONSE:\n", seperator, response, seperator)
    print("DOCUMENTS:\n", seperator)
    for doc in rag_demon.context:
        print(f"Metadata:\n{doc.metadata}\nContent: {doc.page_content}\nScore: {rag_demon.scores[0]}\n")

# Test the application
if __name__ == "__main__":
    main()
