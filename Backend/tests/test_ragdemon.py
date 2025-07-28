# test_your_module.py

import pytest
from unittest.mock import Mock
from langchain_core.documents import Document
from src.ragdemon.app import _retrieve_core

def test_retrieve_core_with_real_document():
    doc1 = Document(page_content="Content of document 1", metadata={"source": "doc1"})
    doc2 = Document(page_content="Content of document 2", metadata={"source": "doc2"})
    mock_docs = [doc1, doc2]

    mock_store = Mock()
    mock_store.similarity_search.return_value = mock_docs

    query = "test query"
    serialized, returned_docs = _retrieve_core(query, mock_store)

    mock_store.similarity_search.assert_called_once_with("test query", k=2)
    assert returned_docs == mock_docs
    expected_serialized = (
        "Source: {'source': 'doc1'}\nContent: Content of document 1\n\n"
        "Source: {'source': 'doc2'}\nContent: Content of document 2"
    )
    assert serialized == expected_serialized