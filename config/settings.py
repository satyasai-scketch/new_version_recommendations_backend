from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from pydantic import Field, field_validator
from typing import Optional
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
VECTORSTORES_DIR = BASE_DIR / "vectorstores"


load_dotenv()

class Settings(BaseSettings):
    # HTTP
    environment: str = "dev"

    # LLM
    llm_provider: str = "GROQ"
    llm_model: str = Field(default="llama-3.1-8b-instant")
    groq_api_key: str = Field(default_factory=lambda: os.getenv("GROQ_API_KEY"))
    openai_api_key: str = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))
    openai_base_url: Optional[str] = Field(default_factory=lambda: os.getenv("OPENAI_BASE_URL", None))

    # Embeddings
    embeddings_provider: str = "openai"
    embeddings_model: str = "text-embedding-3-small"

    # Vector store
    vectorstore_provider: str = "chroma"
    chroma_dir_profiles: str = Field(
        default_factory=lambda: str((VECTORSTORES_DIR / "customer_profile_vectorstore").resolve())
    )
    chroma_dir_products: str = Field(
        default_factory=lambda: str((VECTORSTORES_DIR / "product_catalog_vector_store").resolve())
    )
    chroma_collection_profiles: str = "customer_profiles_collection"
    chroma_collection_products: str = "product_catalog"

    @field_validator("openai_api_key")
    @classmethod
    def _require_openai_key(cls, v):
        if not v:
            raise ValueError("OPENAI_API_KEY is required. Set it in environment or .env")
        return v

class Config:
    env_file = ".env"