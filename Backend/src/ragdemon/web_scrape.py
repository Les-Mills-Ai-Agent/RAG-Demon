from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document
from typing_extensions import List
from typing import Any, List, Tuple
import yaml
import os
from dotenv import load_dotenv
from flatten_json import flatten

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

def split_document(document: dict) -> List[Document]:

    # Step 1: Flatten the JSON
    flattened_json = flatten(document, separator='.')

    # Step 2: Extract markdown-containing entries
    def contains_markdown(text: str) -> bool:
        return any(token in text for token in ["#", "*", "`"])
    
    markdown_entries = {}
    keys_to_remove = []

    for key, value in flattened_json.items():
        if isinstance(value, str) and contains_markdown(value):
            markdown_entries[key] = value
            keys_to_remove.append(key)

    # Step 3: Remove markdown entries from original flattened JSON
    for key in keys_to_remove:
        del flattened_json[key]

    # Step 4: Use RecursiveJsonSplitter on the cleaned flattened JSON
    json_splitter = RecursiveJsonSplitter(max_chunk_size=500)
    splitted_json = json_splitter.create_documents([flattened_json])

    # Add key path metadata to JSON chunks
    for doc in splitted_json:
        doc.metadata["source"] = "json_split"
        # You can add additional metadata here if needed

    # Step 5: Split markdown entries with MarkdownTextSplitter
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
        ("####", "Header 4"),
    ]
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on)
    splitted_md = []

    for key, text in markdown_entries.items():
        chunks = markdown_splitter.split_text(text)
        for chunk in chunks:
            chunk.metadata["source"] = "markdown_split"
            chunk.metadata["key_path"] = key
            splitted_md.append(chunk)

    # Combine all split documents
    return splitted_json + splitted_md

def test():
    with open("sample_data/test_data.yaml", "r") as f:
        return yaml.safe_load(f)

# # Only run self‑test when executed directly, not on import
# if __name__ == "__main__":
#     md, json = separate_markdown_from_yaml(test())
#     print(md)
