import json
from pydantic import BaseModel, Field, ValidationError
from typing import List, Optional
from domain.models import Recommendation, RecommendationResult, ComplementarySet

class ComplementarySchema(BaseModel):
    base_product_id: str
    complements: List[str]

class RecommendationItemSchema(BaseModel):
    product_id: int
    product_name: str
    reason: str

class RecommendationSchema(BaseModel):
    customer_id: Optional[int]
    recommendations: List[RecommendationItemSchema]

class ComplementTagsSchema(BaseModel):
    customer_id: int
    tags: list[str] = Field(min_length=1)

def parse_complement_tags(llm_output: str) -> tuple[int, list[str]]:
    data = json.loads(llm_output)
    model = ComplementTagsSchema.model_validate(data)
    return model.customer_id, model.tags


def parse_complements(llm_output: str) -> ComplementarySet:
    data = json.loads(llm_output)
    model = ComplementarySchema.model_validate(data)
    return ComplementarySet(**model.model_dump())

def parse_recommendations(llm_output: str) -> RecommendationResult:
    # print("LLM Output:", llm_output)
    data = json.loads(llm_output)
    model = RecommendationSchema.model_validate(data)
    return RecommendationResult(
        customer_id=model.customer_id,
        recommendations=[Recommendation(**r.model_dump()) for r in model.recommendations]
    )
