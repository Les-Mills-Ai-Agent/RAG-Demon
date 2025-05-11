
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)
os.getenv("USER_AGENT")
from langchain_community.document_loaders import WebBaseLoader
import yaml

def fetch_documentation(url):
    loader = WebBaseLoader(url)
    doc_list = loader.load()

    document_str = doc_list[0].page_content
    parsed_doc = yaml.safe_load(document_str)
    count = 1
    for key in parsed_doc.items():
        count+=1
        
    print(count)

    

        

document = fetch_documentation("https://api.content.lesmills.com/docs/v1/content-portal-api.yaml")


