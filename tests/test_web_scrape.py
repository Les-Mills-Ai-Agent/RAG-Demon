import pytest
from langchain_core.documents import Document
from dotenv import load_dotenv
from ragdemon.web_scrape import fetch_documentation
from ragdemon.web_scrape import separate_markdown_from_yaml
from ragdemon.web_scrape import split_document
import yaml

# Load environment variables
load_dotenv(override=True)

@pytest.fixture
def test_data():
    with open("sample_data/test_data.yaml", "r") as file:
        return yaml.safe_load(file)
    
@pytest.fixture
def markdown_sections():
    return [
        "# Welcome to how to use Content Portal API\nContent 1\n\n## Hello I am Header 2\nContent 2", 
        "# How to use videos API\nContent 1\n\n## Hello I am Header 2\nContent 2"
    ]

@pytest.fixture
def cleaned_yaml():
    return {
        "openapi": "3.1.0",
        "info": {
            "version": "1.0",
            "title": "Company Content Portal API",
            "description": None
        },
        "paths": {
            "nested": {
                "object": {
                    "description": None
                }
            }
        }
    }

def test_fetch_documentation():
    document = fetch_documentation("https://api.content.lesmills.com/docs/v1/content-portal-api.yaml")

    assert isinstance(document, dict)
    assert document['info']['title'] == "LesMills Content Portal API"
    
def test_separate_markdown_from_yaml(test_data, markdown_sections, cleaned_yaml):
    md, json = separate_markdown_from_yaml(test_data)
    
    assert md == markdown_sections
    assert json == cleaned_yaml
    
    
# Splitting to be improved further in new story

# def test_split_document(test_data):
#     markdown_sections, cleaned_yaml = split_document(test_data)
    
#     assert len(markdown_sections) == 4
#     assert markdown_sections[0].metadata["Header 1"] == "Welcome to how to use Content Portal API"
#     assert markdown_sections[0].page_content == "Content 1"
#     assert markdown_sections[1].metadata["Header 2"] == "Hello I am Header 2"
#     assert markdown_sections[1].page_content == "Content 2"
    
#     assert markdown_sections[2].metadata["Header 1"] == "How to use videos API"
#     assert markdown_sections[2].page_content == "Content 1"
#     assert markdown_sections[3].metadata["Header 2"] == "Hello I am Header 2"
#     assert markdown_sections[3].page_content == "Content 2"
