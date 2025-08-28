from typing import List
from domain.models import RecommendationResult, ComplementarySet, CustomerProfile, Product
from data.repositories import CustomerProfileRepository, ProductCatalogRepository
from helpers.finalize_recommender import finalize_recommendations
from llm.interfaces import LLMClient
from llm.prompts import COMPLEMENT_PROMPT, RECOMMENDATION_PROMPT
from llm.prompt_renderer import PromptRenderer
from llm.parsers import parse_complements, parse_recommendations, RecommendationSchema, ComplementarySchema
from datetime import datetime
from helpers.compact_utilities import _compact_json, _to_llm_item
from helpers.product_filters import drop_already_ordered

class RecommenderService:
    def __init__(
        self,
        llm: LLMClient,
        profiles: CustomerProfileRepository,
        products: ProductCatalogRepository,
        renderer: PromptRenderer
    ):
        self.llm = llm
        self.profiles = profiles
        self.products = products
        self.renderer = renderer

    def get_recommendations(self, customer_id: str, shortlist_k: int = 50) -> RecommendationResult:
        profile: CustomerProfile | None = self.profiles.get_by_customer_id(customer_id)

        current_time = datetime.now()
        if not profile:
            # Return empty but valid structure or raise domain error
            return RecommendationResult(customer_id=customer_id, recommendations=[])
        if profile.profile_text == f"No sufficient data found for customer ID: {customer_id}":
            return RecommendationResult(customer_id=customer_id, recommendations=[])
        
        print("Time taken to profile search: ", datetime.now() - current_time)
        

        current_time = datetime.now()
        shortlist: List[Product] = self.products.search_similar(profile.profile_text, k=shortlist_k)
        print("Time taken to get the products: ", datetime.now() - current_time)
        shortlist = drop_already_ordered(shortlist, profile)

        llm_shortlist = [_to_llm_item(p) for p in shortlist]

        # Build JSON schema strings inline or use OpenAI JSON schema in response_format
        # rec_schema = RecommendationSchema.model_json_schema()

        rec_schema_json = _compact_json(RecommendationSchema.model_json_schema())
        shortlist_json = _compact_json(llm_shortlist)

        prompt = self.renderer.render(
            RECOMMENDATION_PROMPT,
            {
                "profile": profile.profile_text,
                # "shortlist": "[" + ",".join([p.model_dump_json() for p in shortlist]) + "]",
                "shortlist": shortlist_json,
                "json_schema": rec_schema_json
            },
        )

        current_time = datetime.now()
        raw = self.llm.generate(prompt=prompt,top_p=0.0, temperature=0, response_format={"type": "json_object"})
        print("time taken to generate the llm output: ", datetime.now() - current_time)
        parsed = parse_recommendations(raw)
        parsed = finalize_recommendations(parsed, shortlist, k=shortlist_k)
        return parsed

    def get_complements(self, base_product_id: str, behavior_summary: str) -> ComplementarySet:
        comp_schema = ComplementarySchema.model_json_schema()
        prompt = self.renderer.render(
            COMPLEMENT_PROMPT,
            {"behavior": behavior_summary, "json_schema": comp_schema},
        )
        raw = self.llm.generate(prompt=prompt, temperature=0.2)
        return parse_complements(raw)
