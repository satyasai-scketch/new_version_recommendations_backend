import json

def _to_llm_item(p) -> dict:
    # Only what’s needed to decide uniqueness & selection:
    return {
        "product_id": int(getattr(p, "product_id", getattr(p, "id", 0))),
        "name": getattr(p, "product_name", getattr(p, "name", "")),
    }

def _compact_json(obj: dict | list) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))