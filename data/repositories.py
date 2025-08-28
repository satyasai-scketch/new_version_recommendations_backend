from typing import Optional, List
from domain.models import CustomerProfile, Product
from vectorstores.interfaces import VectorStore
from helpers.product_grouping import dedupe_by_group, interleave_by_category
from datetime import datetime

class CustomerProfileRepository:
    def __init__(self, store: VectorStore):
        self.store = store
    
    def get_by_customer_id(self, customer_id: str) -> Optional[CustomerProfile]:
        # Ensure type matches how it was stored in Chroma metadata
        row = self.store.get_one(where={"customer_id": customer_id})
        if not row:
            return None
        d = row
        return CustomerProfile(
            customer_id=d["metadata"]["customer_id"],
            profile_text=d["page_content"],
            metadata=d["metadata"],
        )
    
class ProductCatalogRepository:
    def __init__(self, store: VectorStore):
        self.store = store

    def search_similar(self, text: str, k: int = 50) -> List[Product]:
        current_time = datetime.now()
        results = self.store.max_mmr_search(query=text, k=k)
        products = []
        for r in results:
            md = r["metadata"]
            products.append(Product(
                id=str(md.get("product_id") or md.get("id") or ""),
                name=md.get("name"),
                category=md.get("categories"),
                price=md.get("price", 0.0),
                url=md.get("url", None),
                metadata=md
            ))
        print("time taken to complete the product vector search: ", datetime.now() - current_time)
        current_time = datetime.now()
        products = dedupe_by_group(products)
        products = interleave_by_category(products, k=k, max_per_cat=30)
        print("Time taken to filtering : ", datetime.now() - current_time)
        return products