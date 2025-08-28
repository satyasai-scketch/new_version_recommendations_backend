from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl

class Product(BaseModel):
    id: str
    name: str
    category: Optional[str] = None
    price: float
    url: Optional[HttpUrl] = None
    metadata: dict = Field(default_factory=dict)


class CustomerProfile(BaseModel):
    customer_id: int
    profile_text: str
    vector: Optional[List[float]] = None
    metadata: dict = Field(default_factory=dict)


class Recommendation(BaseModel):
    product_id: int
    product_name: str
    reason: str

class RecommendationResult(BaseModel):
    customer_id: int
    recommendations: List[Recommendation]

class ComplementarySet(BaseModel):
    base_product_id: str
    compliments: List[str]


class ErrorResponse(BaseModel):
    code: str
    message: str
    details: Optional[dict] = None

