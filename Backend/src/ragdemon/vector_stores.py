from abc import ABC, abstractmethod
from langchain_core.documents import Document
from typing import List
from langchain_pinecone import PineconeVectorStore
from pympler import asizeof

class BaseVectorStore(ABC):
    @abstractmethod
    def add_documents(self, documents: List[Document]):
        pass

    @abstractmethod
    def similarity_search(self, query: str, k: int = 2) -> List[tuple[Document, float]]:
        pass

class PineconeStore(BaseVectorStore):
    def __init__(self, index, embeddings):
        self.index = index
        self.embeddings = embeddings
        self.store = PineconeVectorStore(index=self.index, embedding=self.embeddings)

    def add_documents(self, documents: List[Document]):
        # tooBig = []
        # for doc in documents:
        #     size = asizeof.asizeof(doc)
        #     if size > 40960:
        #         tooBig.append(size)
        #         print(doc)
                
        # print(tooBig)

        self.store.add_documents(documents)

    def similarity_search(self, query: str, k: int = 2) -> List[Document]:
        return self.store.similarity_search(query, k=k)