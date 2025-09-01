import html, re, unicodedata
from typing import Any, List, Dict
from collections import defaultdict

COLOR = {
    "black","blue","red","green","grey","gray","white","navy","maroon","purple",
    "orange","pink","brown","beige","yellow","teal","olive","khaki","cream",
    "turquoise","gold","silver","violet","indigo","magenta","cyan"
}
SIZE = {"xxs","xs","s","m","l","xl","xxl","xxxl","2xl","3xl","4xl","5xl"} | {str(n) for n in range(24, 65)}

def _slug(s: str) -> str:
    s = unicodedata.normalize("NFKC", s.lower())
    s = html.unescape(s)
    s = re.sub(r"[^\w\s-]+", "", s)
    s = re.sub(r"\s+", "-", s).strip("-")
    return s

def _base_name(name: str) -> str:
    """Remove trailing size/color tokens like '-XL-Blue' but keep style like '(Crew-neck)'."""
    parts = re.split(r"[-_/]", html.unescape(name))
    keep, dropped = [], 0
    for token in reversed(parts):
        t = token.strip().lower()
        if dropped < 2 and (t in COLOR or t in SIZE):
            dropped += 1
            continue
        keep.append(token)
    base = "-".join(reversed(keep)).strip("- ")
    base = re.sub(r"\s+", " ", base).strip()
    return base

def group_key_from_doc(doc: Any) -> str:
    """Build a stable 'base product' key from a LangChain Document OR your domain Product."""
    meta = getattr(doc, "metadata", None) or {}
    name = meta.get("name") or getattr(doc, "product_name", None) or getattr(doc, "name", "")
    if not name and getattr(doc, "page_content", ""):
        m = re.search(r"^Name:\s*(.+)$", doc.page_content, flags=re.MULTILINE)
        if m:
            name = m.group(1)
    base = _base_name(name)
    return "name:" + _slug(base)

def dedupe_by_group(items: List[Any]) -> List[Any]:
    seen, out = set(), []
    for it in items:
        gk = group_key_from_doc(it)
        if gk in seen:
            continue
        seen.add(gk)
        out.append(it)
    return out

def _item_category(it: Any) -> str:
    """Normalize category from metadata['categories'] → .category → .product_category → 'unknown'."""
    meta = getattr(it, "metadata", None) or {}
    cat = meta.get("categories") or getattr(it, "category", None) or getattr(it, "product_category", None) or "unknown"
    cat = (cat or "").strip() or "unknown"
    if cat.lower() in {"no categories", "none", "null"}:
        cat = "unknown"
    return cat

import math

def pick_max_per_cat(items: List[Any], k: int = 50, min_total: int = 15) -> int:
    """
    Adaptive max_per_cat:
    - Ensures it's large enough to hit target k given category count
    - Ensures at least min_total items can be drawn even if categories are few
    """
    cats = { _item_category(i) for i in items }
    C = max(1, len(cats))
    need_for_k = math.ceil(k / C)
    need_for_floor = math.ceil(min_total / C)
    return max(need_for_k, need_for_floor)



def interleave_by_category(items: List[Any], k: int, max_per_cat: int = 3) -> List[Any]:
    """
    Round-robin across categories to avoid a single category dominating.
    Always terminates:
      - Computes true capacity (sum of min(len(bucket), max_per_cat)).
      - Caps target to capacity.
      - Breaks if a full round makes no progress.
    """
    # Bucketize
    buckets: Dict[str, List[Any]] = defaultdict(list)
    for it in items:
        buckets[_item_category(it)].append(it)

    # True max we can output given per-category cap
    capacity = sum(min(len(lst), max_per_cat) for lst in buckets.values())
    target = min(k, capacity)

    out: List[Any] = []
    per_cat_count: Dict[str, int] = {c: 0 for c in buckets}
    cats = list(buckets.keys())

    # Prefer deterministic ordering: move 'unknown' last if present
    if "unknown" in cats:
        cats = [c for c in cats if c != "unknown"] + ["unknown"]

    while len(out) < target:
        made_progress = False
        for cat in cats:
            if len(out) >= target:
                break
            if per_cat_count[cat] >= max_per_cat:
                continue
            if not buckets[cat]:
                continue
            out.append(buckets[cat].pop(0))
            per_cat_count[cat] += 1
            made_progress = True
        if not made_progress:
            # No bucket could contribute this round (all empty or at cap).
            break

    return out
