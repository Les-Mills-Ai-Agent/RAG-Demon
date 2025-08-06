import os
import json
import yaml
import pdfplumber
from bs4 import BeautifulSoup

def detect_file(path: str) -> str:
    return os.path.splitext(path)[1].lower()

def parse_file(path: str) -> dict:
    file_type = detect_file(path)
    
    if file_type == '.json':
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    elif file_type == '.yaml' or file_type == '.yml':
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
        
    elif file_type == '.md':
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            return {"content": content}

    
    elif file_type == '.pdf':
        with pdfplumber.open(path) as pdf:
            text = ''
            for page in pdf.pages:
                text += page.extract_text() + '\n'
            return {"content": text.strip()}
    
    elif file_type == '.html':
        with open(path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
            return {"content": soup.get_text(separator='\n').strip()}
    
    else:
        raise ValueError(f"Unsupported file type: {file_type}")