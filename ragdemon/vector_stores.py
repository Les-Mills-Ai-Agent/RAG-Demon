from abc import ABC, abstractmethod
from langchain_core.documents import Document
from typing import List
from langchain_core.vectorstores import InMemoryVectorStore

class BaseVectorStore(ABC):
    @abstractmethod
    def add_documents(self, documents: List[Document]):
        pass

    @abstractmethod
    def similarity_search_with_scores(self, query: str, k: int = 2) -> List[tuple[Document, float]]:
        pass

class InMemoryStore(BaseVectorStore):
    def __init__(self, embeddings):
        self.embeddings = embeddings
        self.store = InMemoryVectorStore(embedding=self.embeddings)

    def add_documents(self, documents: List[Document]):
        self.store.add_documents(documents)

    def similarity_search_with_scores(self, query: str, k: int = 2) -> List[tuple[Document, float]]:
        return self.store.similarity_search_with_score(query, k=k)