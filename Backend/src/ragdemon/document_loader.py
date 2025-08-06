from parsing import parse_file
from chunking import split_document
from langchain_core.documents import Document

def parse_and_split(path: str) -> list[Document]:
    parsed = parse_file(path)
    return split_document(parsed)