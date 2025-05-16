from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document
from typing_extensions import List
from typing import Any, List, Tuple
import yaml
import os
from dotenv import load_dotenv

from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    MarkdownHeaderTextSplitter,
    RecursiveJsonSplitter,
)

# Load environment variables
load_dotenv(override=True)
os.getenv("USER_AGENT")


def fetch_documentation(url: str) -> dict:
    loader = WebBaseLoader(url)
    doc_list = loader.load()

    document_str = doc_list[0].page_content
    parsed_doc = yaml.safe_load(document_str)

    return parsed_doc

# This recursive function breaks down the parsed yaml document from https://api.content.lesmills.com/docs/v1/content-portal-api.yaml
# And returns: list of nested markdown snippets, and dictionary of the cleaned "yaml" structure without the markdown
def separate_markdown_from_yaml(obj: Any) -> Tuple[List[str], Any]:
    def contains_markdown(text: str) -> bool:
        return any(token in text for token in ["#", "*", "`"])
    
    if isinstance(obj, str):
        if contains_markdown(obj):
            return [obj], None
        else:
            return [], obj
        
    if isinstance(obj, list):
        md_list = []
        cleaned_list = []
        
        for item in obj:
            md, cleaned = separate_markdown_from_yaml(item)
            md_list.extend(md)
            if cleaned:
                cleaned_list.append(cleaned)
        
        return md_list, cleaned_list
    
    if isinstance(obj, dict):
        md_list = []
        cleaned_obj = {}
        
        for key, value in obj.items():
            md, cleaned = separate_markdown_from_yaml(value)
            md_list.extend(md)
            if cleaned:
                cleaned_obj[key] = cleaned
        
        return md_list, cleaned_obj
    
    return [], obj            


def split_document(document: dict) -> List[Document]:

    # Retrieve nested Markdown snippets, and the cleaned YAML structure without Markdown
    markdown_strings, cleaned_yaml = separate_markdown_from_yaml(document)
    
    # Create JSON splits
    json_splitter = RecursiveJsonSplitter(max_chunk_size=500)
    json_docs = json_splitter.create_documents([cleaned_yaml])

    # Create Markdown splits
    combined_markdown = "\n\n".join(markdown_strings)

    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
        ("####", "Header 4"),
    ]

    md_splitter = MarkdownHeaderTextSplitter(headers_to_split_on)
    md_splits = md_splitter.split_text(combined_markdown)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=50,
        separators=[". ", "\n\n", "\n"],
    )

    md_docs = text_splitter.split_documents(md_splits)

    # Combine and return both JSON and Markdown splits
    return json_docs + md_docs
