from langchain_community.document_loaders import WebBaseLoader
import bs4
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
)

splitter = RecursiveCharacterTextSplitter(
    chunk_size=400,
    chunk_overlap=50,
    keep_separator=False,

)

loader = WebBaseLoader(
    [
    "https://lesmillsvirtualapp.freshdesk.com/en/support/solutions/articles/36000491544-club-customer-faqs-",
    "https://lesmillsvirtualapp.freshdesk.com/en/support/solutions/articles/36000527862-implementation-faqs",
    "https://lesmillsvirtualapp.freshdesk.com/en/support/solutions/articles/36000498749-terms-of-use-content-portal",
    "https://lesmillsvirtualapp.freshdesk.com/en/support/solutions/articles/36000498750-privacy-policy-content-portal",
    ]
)

documents = loader.load()

splits = splitter.split_documents(documents)

bs4.BeautifulSoup().get_text()