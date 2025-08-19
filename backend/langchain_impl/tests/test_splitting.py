from langchain_core.documents import Document
from dotenv import load_dotenv

from langchain_impl.splitting import split_document

# Load environment variables
load_dotenv(override=True)

def test_split_document():
    document = Document(page_content="# Hello I am Header 1\nContent 1\n\n## Hello I am Header 2\nContent 2")
    splits = split_document(document.page_content)
    
    assert len(splits) == 2
    assert splits[0].page_content == "Content 1"
    assert splits[0].metadata["Header 1"] == "Hello I am Header 1"
    assert splits[1].page_content == "Content 2"
    assert splits[1].metadata["Header 2"] == "Hello I am Header 2"