import pytest
from unittest.mock import MagicMock, patch
from langchain_core.documents import Document
from ragdemon.ragdemon import RagDemon
from langchain_openai import ChatOpenAI
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

def test_init_creates_llm_embeddings_and_vectorstore():
    rag_demon = RagDemon()
    assert isinstance(rag_demon.llm, ChatOpenAI)
    assert isinstance(rag_demon.embeddings, OpenAIEmbeddings)
    assert isinstance(rag_demon.vector_store, InMemoryVectorStore)