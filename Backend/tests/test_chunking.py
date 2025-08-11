from src.ragdemon.chunking import split_document
from langchain_core.documents import Document
import pytest
import json

# test splitting a dict containing markdown text
def test_split_dict_with_markdown():
    doc = {
        "title": "Example",
        "description": "# Header\nSome content"
    }
    chunks = split_document(doc)
    assert any(isinstance(chunk, Document) for chunk in chunks)
    assert any("Some content" in chunk.page_content for chunk in chunks)

# test splitting a long string into multiple chunks
def test_split_string():
    chunks = split_document("This is a sentence. " * 1000)
    assert all(isinstance(c, Document) for c in chunks)
    assert len(chunks) > 1

# test splitting a dict with a 'content' key containing text
def test_split_dict_with_content_key():
    chunks = split_document({"content": "test data."})
    content = json.loads(chunks[0].page_content)
    assert content["content"] == "test data."

# tests splitting unsupported types raises an error
def test_split_invalid_type():
    with pytest.raises(ValueError):
        split_document(123)