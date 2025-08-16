import pytest
from langchain_core.documents import Document
from dotenv import load_dotenv
from src.ragdemon.web_scrape import fetch_documentation
from src.ragdemon.web_scrape import split_document
import yaml

# Load environment variables
load_dotenv(override=True)

@pytest.fixture
def test_data():
    with open("../sample_data/test_data.yaml", "r") as file:
        return yaml.safe_load(file)

def test_fetch_documentation():
    document = fetch_documentation("https://api.content.lesmills.com/docs/v1/content-portal-api.yaml")

    assert isinstance(document, dict)
    assert document['info']['title'] == "LesMills Content Portal API"
    
def test_split_document(test_data):
    splits = split_document(test_data)
    
    # First split (json_split)
    assert splits[0].metadata["source"] == "json_split"
    assert splits[0].page_content == '{"openapi": "3.1.0", "info.version": "1.0", "info.title": "Company Content Portal API"}'

    # Second split (markdown_split - info.description, Header 1 only)
    assert splits[1].metadata["source"] == "markdown_split"
    assert splits[1].metadata["Header 1"] == "Welcome to how to use Content Portal API"
    assert splits[1].metadata["key_path"] == "info.description"
    assert splits[1].page_content == "Content 1"

    # Third split (markdown_split - info.description, Header 1 + Header 2)
    assert splits[2].metadata["source"] == "markdown_split"
    assert splits[2].metadata["Header 1"] == "Welcome to how to use Content Portal API"
    assert splits[2].metadata["Header 2"] == "Hello I am Header 2"
    assert splits[2].metadata["key_path"] == "info.description"
    assert splits[2].page_content == "Content 2"

    # Fourth split (markdown_split - Videos API, Header 1 only)
    assert splits[3].metadata["source"] == "markdown_split"
    assert splits[3].metadata["Header 1"] == "How to use videos API"
    assert splits[3].metadata["key_path"] == "paths.items/Videos.get.description"
    assert splits[3].page_content == "Content 1"

    # Fifth split (markdown_split - Videos API, Header 1 + Header 2)
    assert splits[4].metadata["source"] == "markdown_split"
    assert splits[4].metadata["Header 1"] == "How to use videos API"
    assert splits[4].metadata["Header 2"] == "Hello I am Header 2"
    assert splits[4].metadata["key_path"] == "paths.items/Videos.get.description"
    assert splits[4].page_content == "Content 2"