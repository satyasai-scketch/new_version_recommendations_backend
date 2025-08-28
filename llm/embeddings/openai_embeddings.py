from typing import Optional
from llm.interfaces import EmbeddingsClient
from langchain_openai import OpenAIEmbeddings as LCOpenAIEmbeddings


class OpenAIEmbeddings(EmbeddingsClient):
    """
    Wrapper around langchain_openai.OpenAIEmbeddings
    to conform to our EmbeddingsClient interface.
    """

    def __init__(
        self,
        api_key: str,
        model: str,
        base_url: Optional[str] = None,
    ):
        """
        Args:
            api_key: OpenAI (or compatible) API key
            model: embedding model name (e.g., "text-embedding-3-large")
            base_url: optional custom endpoint (e.g., OpenRouter base URL)
        """
        self._emb = LCOpenAIEmbeddings(
            api_key=api_key,
            model=model,
        )

    def embed(self, texts: list[str]) -> list[list[float]]:
        # langchain_openai's OpenAIEmbeddings returns a list of vectors
        return self._emb.embed_documents(texts)

    def embed_one(self, text:str) -> list[float]:
        return self._emb.embed_query(text)
    
    @property
    def lc(self) -> LCOpenAIEmbeddings:
        return self._emb