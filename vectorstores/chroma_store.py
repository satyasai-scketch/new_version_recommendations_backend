from vectorstores.interfaces import VectorStore
from langchain_chroma import Chroma
from typing import Optional, Any, List, Tuple
from langchain_core.documents import Document

class ChromaStore(VectorStore):
    def __init__(self, collection_name: str, persist_dir: str, embedding_lc):
        self._store = Chroma(
            collection_name = collection_name,
            persist_directory= persist_dir,
            embedding_function= embedding_lc
        )


    def add_texts(self, texts, metadatas, ids):
        self._store.add_texts(texts=texts, metadatas=metadatas, ids= ids)

    def similarity_search(self, query: str, k: int= 5, metadata_filter: Optional[dict] = None):
        docs: list[Document] = self._store.similarity_search(query, k=k, filter= metadata_filter)
        return [ {"page_content": d.page_content, "metadata": d.metadata, "id": getattr(d, "id", None)} for d in docs ]

    def similarity_search_by_vector(self, vector, k:int = 5, metadata_filter: Optional[dict] = None):
        docs: list[Document] = self._store.similarity_search_by_vector(vector, k=k, filter= metadata_filter)
        return [ {"page_content": d.page_content, "metadata": d.metadata, "id": getattr(d, "id", None)} for d in docs ]
    
    def similarity_search_with_score(self, query: str, k: int = 1, filter: Optional[dict] = None) -> list[dict[str, Any]]:
        docs_and_scores: List[Tuple[Document, float]] = self._store.similarity_search_with_score(
            query, k=k, filter=filter
        )
        return [
            {
                "page_content": d.page_content,
                "metadata": d.metadata,
                "id": getattr(d, "id", None),
            }
            for d, score in docs_and_scores
        ]
    
    def max_mmr_search(
        self, query: str, k: int = 50, fetch_k: int = 105, lambda_mult: float = 0.2, metadata_filter: Optional[dict] = None
    ) -> List[Document]:
        """Diverse retrieval via Max Marginal Relevance (MMR)."""
        docs: list[Document] = self._store.max_marginal_relevance_search(
            query=query,
            k=k,                     # final desired count
            fetch_k=fetch_k,         # pool size to diversify from
            lambda_mult=lambda_mult, # lower -> more diversity (0.2–0.4 is good)
            filter=metadata_filter,
        )
        return [ {"page_content": d.page_content, "metadata": d.metadata, "id": getattr(d, "id", None)} for d in docs ]
    

    def get_one(self, where: dict) -> Optional[dict]:
        """
        Direct metadata fetch via underlying Chroma collection.
        Avoids embedding & similarity search.
        """
        col = self._store._collection  # accessing wrapped collection
        # Only request allowed fields; 'ids' is returned by default.
        res = col.get(where=where, include=['metadatas', 'documents'])
        if not res or not res.get("ids"):
            return None
        i = 0
        return {
            "id": res["ids"][i],
            "page_content": (res.get("documents") or [None])[i],
            "metadata": (res.get("metadatas") or [{}])[i],
        }