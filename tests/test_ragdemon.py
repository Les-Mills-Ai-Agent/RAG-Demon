import pytest
from unittest.mock import MagicMock, patch
from langchain_core.documents import Document
from ragdemon.ragdemon import RagDemon
from langchain_openai import ChatOpenAI
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore


def test_init_creates_llm_embeddings_and_vectorstore():
    rag_demon = RagDemon()
    assert isinstance(rag_demon.llm, ChatOpenAI)
    assert isinstance(rag_demon.embeddings, OpenAIEmbeddings)
    assert isinstance(rag_demon.vector_store, InMemoryVectorStore)

def test_split_document():
    rag_demon = RagDemon()
    document = Document(page_content="# Hello I am Header 1\nContent 1\n\n## Hello I am Header 2\nContent 2")
    splits = rag_demon.split_and_store_document(document.page_content)
    
    assert len(splits) == 2
    assert splits[0].page_content == "Content 1"
    assert splits[0].metadata["Header 1"] == "Hello I am Header 1"
    assert splits[1].page_content == "Content 2"
    assert splits[1].metadata["Header 2"] == "Hello I am Header 2"