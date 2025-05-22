from langchain_core.documents import Document
from ragdemon.vector_stores import InMemoryStore  # replace with your actual module
from langchain_core.embeddings import FakeEmbeddings  # replace with your actual module

def test_in_memory_store_add_and_search():
    # Use the embedding wrapper
    store = InMemoryStore(embeddings=FakeEmbeddings(size=100))

    # Create documents
    doc1 = Document(page_content="apple", metadata={"id": 1})
    doc2 = Document(page_content="banana", metadata={"id": 2})
    doc3 = Document(page_content="apricot", metadata={"id": 3})
    docs = [doc1, doc2, doc3]

    # Add documents
    store.add_documents(docs)

    # Search
    results = store.similarity_search("apple", k=2)

    assert isinstance(results, list)
    assert len(results) == 2
    for doc in results:
        assert isinstance(doc, Document)
        assert isinstance(doc.page_content, str)
        assert isinstance(doc.metadata, dict)

    # Top result should match "apple" or something close
    top_content = results[0].page_content
    assert top_content in {"apple", "apricot"}