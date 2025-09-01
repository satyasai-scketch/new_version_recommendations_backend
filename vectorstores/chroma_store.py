from typing import Optional, Any, List, Callable
from langchain_chroma import Chroma
from langchain_core.documents import Document
from chromadb.errors import NotFoundError
from vectorstores.interfaces import VectorStore

class ChromaStore(VectorStore):
    """
    Stateless, resilient Chroma wrapper:
    - Resolves a fresh Chroma vectorstore per call (cheap).
    - Retries once on NotFoundError (collection UUID changed after DAG swap).
    """

    def __init__(self, collection_name: str, persist_dir: str, embedding_lc):
        self.collection_name = collection_name
        self.persist_dir = persist_dir
        self.embedding_lc = embedding_lc

    def _new_store(self) -> Chroma:
        return Chroma(
            collection_name=self.collection_name,
            persist_directory=self.persist_dir,
            embedding_function=self.embedding_lc,
        )

    def _with_store(self, fn: Callable[[Chroma], Any]) -> Any:
        # First attempt
        store = self._new_store()
        try:
            return fn(store)
        except NotFoundError:
            # Re-open once; DAG likely flipped the underlying store
            store = self._new_store()
            return fn(store)

    # ---- VectorStore Protocol methods ----

    def add_texts(self, texts: List[str], metadatas: List[dict], ids: List[str]) -> None:
        def _run(store: Chroma):
            store.add_texts(texts=texts, metadatas=metadatas, ids=ids)
        return self._with_store(_run)

    def similarity_search(self, query: str, k: int = 5, metadata_filter: Optional[dict] = None) -> List[dict]:
        def _run(store: Chroma):
            docs: List[Document] = store.similarity_search(query, k=k, filter=metadata_filter)
            return [
                {"id": d.metadata.get("id") or d.metadata.get("product_id"), "page_content": d.page_content, "metadata": d.metadata}
                for d in docs
            ]
        return self._with_store(_run)

    def similarity_search_by_vector(self, vector: List[float], k: int = 5, metadata_filter: Optional[dict] = None) -> List[dict]:
        def _run(store: Chroma):
            docs: List[Document] = store.similarity_search_by_vector(embedding=vector, k=k, filter=metadata_filter)
            return [
                {"id": d.metadata.get("id") or d.metadata.get("product_id"), "page_content": d.page_content, "metadata": d.metadata}
                for d in docs
            ]
        return self._with_store(_run)

    def similarity_search_with_score(self, query: str, k: int = 1, filter: Optional[dict] = None) -> List[dict]:
        def _run(store: Chroma):
            pairs = store.similarity_search_with_score(query, k=k, filter=filter)
            out = []
            for d, score in pairs:
                out.append({
                    "id": d.metadata.get("id") or d.metadata.get("product_id"),
                    "page_content": d.page_content,
                    "metadata": d.metadata,
                    "score": float(score),
                })
            return out
        return self._with_store(_run)

    def max_mmr_search(
        self, query: str, k: int = 50, fetch_k: int = 105, lambda_mult: float = 0.2, metadata_filter: Optional[dict] = None
    ) -> List[dict]:
        def _run(store: Chroma):
            docs: List[Document] = store.max_marginal_relevance_search(
                query, k=k, fetch_k=fetch_k, lambda_mult=lambda_mult, filter=metadata_filter
            )
            return [
                {"id": d.metadata.get("id") or d.metadata.get("product_id"), "page_content": d.page_content, "metadata": d.metadata}
                for d in docs
            ]
        return self._with_store(_run)

    def get_one(self, where: dict) -> Optional[dict]:
        """
        Direct metadata fetch via underlying Chroma collection
        (avoids embeddings). We go through the wrapped collection.
        """
        def _run(store: Chroma):
            col = store._collection  # underlying chromadb Collection
            res = col.get(where=where, include=['metadatas', 'documents'])
            if not res or not res.get("ids"):
                return None
            i = 0
            return {
                "id": res["ids"][i],
                "page_content": (res.get("documents") or [None])[i],
                "metadata": (res.get("metadatas") or [{}])[i],
            }
        return self._with_store(_run)
