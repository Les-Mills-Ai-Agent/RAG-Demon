from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document
from typing_extensions import List
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


def fetch_documentation(url):
    loader = WebBaseLoader(url)
    doc_list = loader.load()

    document_str = doc_list[0].page_content
    parsed_doc = yaml.safe_load(document_str)

    return [parsed_doc]


def extract_markdown(obj):
    md_sections = []

    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, str) and any(
                token in value for token in ["#", "*", "`"]
            ):
                md_sections.append(value)
            elif isinstance(value, (dict, list)):
                md_sections.extend(extract_markdown(value))

    elif isinstance(obj, list):
        for item in obj:
            md_sections.extend(extract_markdown(item))

    return md_sections


def split_document(document) -> List[Document]:

    # Create JSON splits
    json_splitter = RecursiveJsonSplitter(max_chunk_size=1000)
    json_docs = json_splitter.create_documents(document)

    # Retrieve nested Markdown snippets
    markdown_strings = extract_markdown(document)
    combined_markdown = "\n\n".join(markdown_strings)

    # Create Markdown splits
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
