COMPLEMENT_PROMPT = """\
You are a product assistant. Given a customer's behavior summary and a catalog,
suggest complementary product IDs for the customer to consider.

Customer behavior:
{behavior}

Output strictly as JSON with the following schema:
{json_schema}
"""

RECOMMENDATION_PROMPT = """\
Given the customer profile and a shortlist, choose exactly 10 distinct products.

# Constraints (must follow)
- **Does not include previously purchased products**
- **Uniqueness:** At most one per base product (treat size/color variants as the same; drop variants).
- Prefer items most aligned with the profile intent.
- **Reason brevity:** Each reason ≤ 10 words, no filler.
- **Diversity:** Include a mix of categories and styles.

Customer profile (brief):
{profile}

Shortlist (JSON; objects with product_id, name only):
{shortlist}

Output strictly as JSON matching this schema without changing the datatypes:
{json_schema}

Output requirements (STRICT):
- Output ONE JSON object only, no explanation, no code fences.
- The ONLY allowed keys are: "customer_id", "recommendations".
- Inside "recommendations", each item has ONLY: "product_id", "product_name", "reason".
- Do NOT include "$defs", "schema", "format_instructions", or any additional keys.

Invalid example (do NOT do this):
{{
  "$defs": {{...}},   // forbidden
  "customer_id": 114,
  "recommendations": [ ... ]
}}

Valid example:
{{
  "customer_id": 114,
  "recommendations": [
    {{"product_id": 20344, "product_name": "Nike ...", "reason": "…"}},
    ...
  ]
}}
"""


COMPLEMENT_TAGS_PROMPT = """\
You are a retail merchandiser. Given a customer's profile/behavior summary, list complementary product CATEGORY TAGS that would likely be purchased together with the customer’s interests. 
- Use category tags that actually exist in our catalog taxonomy (short, lowercase, hyphen/underscore ok).
- Return 5–12 tags max, sorted by relevance.

Customer profile/behavior:
{profile}

Output strictly as JSON with this schema:
{json_schema}
"""
