from langchain_core.documents import Document
from src.ragdemon.vector_stores import PineconeStore  # replace with your actual module
from unittest.mock import Mock

def test_pinecone_store_add_and_search():
    # Mock embedding model and index
    mock_embeddings = Mock()
    mock_index = Mock()

    # Mock PineconeVectorStore with mocked methods
    mock_vector_store = Mock()
    mock_vector_store.add_documents = Mock()
    
    mock_docs = [
        Document(page_content="apple", metadata={"id": 1}),
        Document(page_content="apricot", metadata={"id": 3})
    ]
    mock_vector_store.similarity_search = Mock(return_value=mock_docs)

    # Create PineconeStore and override internal store with mock
    pinecone_store = PineconeStore(index=mock_index, embeddings=mock_embeddings)
    pinecone_store.store = mock_vector_store  # Inject the mock

    # Create documents
    docs = [
        Document(page_content="apple", metadata={"id": 1}),
        Document(page_content="banana", metadata={"id": 2}),
        Document(page_content="apricot", metadata={"id": 3}),
    ]

    # Test methods
    pinecone_store.add_documents(docs)
    mock_vector_store.add_documents.assert_called_once_with(docs)

    results = pinecone_store.similarity_search("apple", k=2)
    mock_vector_store.similarity_search.assert_called_once_with("apple", k=2)

    # Assertions on results
    assert isinstance(results, list)
    assert len(results) == 2
    for doc in results:
        assert isinstance(doc, Document)
        assert isinstance(doc.page_content, str)
        assert isinstance(doc.metadata, dict)