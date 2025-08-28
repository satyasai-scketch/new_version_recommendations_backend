from typing import Protocol, Any, Optional

class VectorStore(Protocol):
    def add_texts(self, texts: list[str], metadatas: list[dict], ids: list[str]) -> None:
        ...

    def similarity_search(self, query: str, k:int = 5, metadata_filter: Optional[dict]= None) -> list[dict]:
        ...

    def similarity_search_by_vector(self, vector: list[float], k:int =5, metadata_filter: Optional[dict] = None) -> list[dict]:
        ...
    
    def similarity_search_with_score(self, query: str, k:int=1, filter: Optional[dict]=None) -> list[dict[str, Any]]:
        ...

    def max_mmr_search(
        self, query: str, k: int = 50, fetch_k: int = 105, lambda_mult: float = 0.2, metadata_filter: Optional[dict] = None
    ) -> list[dict[str, Any]]:
        ... 

    def get_one(self, where: dict) -> Optional[dict]: 
        ...