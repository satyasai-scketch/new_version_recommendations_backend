import re
from typing import List, Set
from domain.models import Product, CustomerProfile
from helpers.product_grouping import _base_name

def _ordered_names_from_profile_text(txt: str) -> Set[str]:
    """
    Robustly extract ordered product names from:
    '... placed orders for 'A', 'B', ..., 'Z', viewed products like ...'
    """
    if not txt:
        return set()

    # 1) find the substring between "placed orders for" and "viewed products like"
    start = re.search(r"placed orders for", txt, flags=re.IGNORECASE)
    if not start:
        return set()
    # end marker; if missing, go to end of string
    end = re.search(r"viewed products like", txt, flags=re.IGNORECASE)
    segment = txt[start.end(): end.start()] if end else txt[start.end():]

    # 2) extract all single-quoted names in that segment
    names = re.findall(r"'([^']+)'", segment)

    # 3) normalize with base-name (drops size/color), casefold
    return {_base_name(n).lower() for n in names if n.strip()}

def drop_already_ordered(products: List[Product], profile: CustomerProfile) -> List[Product]:
    """
    Remove products already purchased by the customer.
    Uses product_id first (when available later), then base-name fallback.
    """
    # OPTIONAL: if you enrich profile with exact order IDs later:
    ordered_ids: Set[str] = set(profile.metadata.get("ordered_product_ids", [])) if getattr(profile, "metadata", None) else set()
    ordered_ids = {str(x).strip() for x in ordered_ids if str(x).strip()}

    ordered_names = _ordered_names_from_profile_text(profile.profile_text)

    out = []
    for p in products:
        pid = str(p.metadata.get("product_id") or p.id or "").strip()
        base = _base_name(p.name or "").lower()

        if pid and pid in ordered_ids:
            continue
        if base and base in ordered_names:
            continue
        out.append(p)
    return out
