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
    return ["## This is markdown", "## This is markdown"]

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
    md, cleaned = separate_markdown_from_yaml(test_data)
    
    assert md == markdown_sections
    assert cleaned == cleaned_yaml
    
# def test_split_document(test_data):
#     markdown_sections, cleaned_yaml = split_document(test_data)
    
#     for key, value in markdown_sections:
#         assert value in ["#", "*", "`"]
        
#     assert cleaned_yaml