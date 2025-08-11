from typing import Any, List, Tuple
from langchain_core.documents import Document
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    MarkdownHeaderTextSplitter,
    RecursiveJsonSplitter,
)

def separate_markdown_from_yaml(obj: Any) -> Tuple[List[str], Any]:
    def contains_markdown(text: str) -> bool:
        return any(token in text for token in ["#", "*", "`"])
    
    if isinstance(obj, str):
        if contains_markdown(obj):
            obj = obj.replace("\\n", "\n")
            return [obj], None
        else:
            return [], obj
        
    if isinstance(obj, list):
        md_list = []
        cleaned_list = []
        
        for item in obj:
            md, cleaned = separate_markdown_from_yaml(item)
            md_list. extend(md)
            cleaned_list.append(cleaned)
        
        return md_list, cleaned_list
    
    if isinstance(obj, dict):
        md_list = []
        cleaned_obj = {}
        
        for key, value in obj.items():
            md, cleaned = separate_markdown_from_yaml(value)
            md_list.extend(md)
            cleaned_obj[key] = cleaned
        
        return md_list, cleaned_obj
    
    return [], obj

def split_document(document: Any) -> List[Document]:
    if isinstance(document, dict):
        markdown_strings, cleaned_yaml = separate_markdown_from_yaml(document)

        json_splitter = RecursiveJsonSplitter(max_chunk_size=500)
        json_docs = json_splitter.create_documents([cleaned_yaml])

        combined_markdown = "\n\n".join(markdown_strings)

        markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=[
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
            ("####", "Header 4"),
        ])

        markdown_splits = markdown_splitter.split_text(combined_markdown)

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=50,
            separators=[". ", "\n", "\n\n"]
        )

        markdown_docs = text_splitter.split_documents(markdown_splits)
        return json_docs + markdown_docs
    
    elif isinstance(document, str) or (isinstance(document, dict) and "content" in document):

        text = document.get("content", "") if isinstance(document, dict) else document

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=50,
            separators=[". ", "\n", "\n\n"]
        )

        docs = text_splitter.create_documents([text])
        return docs
    
    else: 
        raise ValueError("Unsupported document type for splitting.")