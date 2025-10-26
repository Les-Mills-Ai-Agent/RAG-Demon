from abc import ABC, abstractmethod
from langchain_core.documents import Document
from typing import List
from langchain_core.vectorstores import InMemoryVectorStore

class BaseVectorStore(ABC):
    @abstractmethod
    def add_documents(self, documents: List[Document]):
        pass

    @abstractmethod
    def similarity_search(self, query: str, k: int = 2) -> List[Document]:
        pass

class InMemoryStore(BaseVectorStore):
    def __init__(self, embeddings):
        self.embeddings = embeddings
        self.store = InMemoryVectorStore(embedding=self.embeddings)

    def add_documents(self, documents: List[Document]):
        self.store.add_documents(documents)

    def similarity_search(self, query: str, k: int = 2) -> List[Document]:
        return self.store.similarity_search(query, k=k)