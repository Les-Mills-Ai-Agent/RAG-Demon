import pytest
from unittest.mock import MagicMock, patch
from langchain_core.documents import Document
from ragdemon.ragdemon import init, split_document, retrieve, generate, State


def test_init_returns_expected_objects():
    llm, embeddings, vector_store = init()
    assert hasattr(llm, "invoke")
    assert hasattr(embeddings, "embed_query")
    assert hasattr(vector_store, "similarity_search_with_score")


def test_split_document_returns_documents():
    example_md = "# Title\nSome introductory text.\n\n## Subheader\nMore details here."
    result = split_document(example_md)

    assert isinstance(result, list)
    assert all(isinstance(doc, Document) for doc in result)
    assert len(result) > 0


def test_retrieve_with_mocked_vectorstore():
    mock_state = {"question": "What is the title?", "context": [], "answer": "", "scores": []}

    fake_doc = Document(page_content="Fake content", metadata={})
    fake_score = 0.9

    with patch("ragdemon.ragdemon.vector_store.similarity_search_with_score", return_value=[(fake_doc, fake_score)]):
        output = retrieve(mock_state)

    assert "context" in output
    assert "scores" in output
    assert output["context"][0].page_content == "Fake content"
    assert output["scores"][0] == fake_score