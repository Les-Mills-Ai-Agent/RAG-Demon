from langchain_openai import ChatOpenAI
from langchain_openai.embeddings import OpenAIEmbeddings

def build_llm_client() -> ChatOpenAI:
    return ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )

def build_embeddings_client() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(
        model="text-embedding-3-large",
    )