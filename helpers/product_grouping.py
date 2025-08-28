import html, re, unicodedata
from typing import Any, List

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
    # Try common shapes: Document.metadata['name'] or Product.product_name/name
    meta = getattr(doc, "metadata", None) or {}
    name = meta.get("name") or getattr(doc, "product_name", None) or getattr(doc, "name", "")
    if not name and getattr(doc, "page_content", ""):
        m = re.search(r"^Name:\s*(.+)$", doc.page_content, flags=re.MULTILINE)
        if m: name = m.group(1)
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

def interleave_by_category(items: List[Any], k: int, max_per_cat: int = 3) -> List[Any]:
    """Round-robin across categories to avoid a single category dominating."""
    # Expect category in doc.metadata['categories'] or item.categories
    buckets = {}
    for it in items:
        meta = getattr(it, "metadata", None) or {}
        cat = meta.get("categories") or getattr(it, "product_category", None) or "unknown"
        buckets.setdefault(cat, []).append(it)
    out = []
    while len(out) < k and any(buckets.values()):
        for cat in list(buckets):
            if not buckets[cat]:
                continue
            if sum(1 for x in out if ((getattr(x, "metadata", None) or {}).get("categories") 
                                       or getattr(x, "product_category", None) or "unknown") == cat) >= max_per_cat:
                continue
            out.append(buckets[cat].pop(0))
            if len(out) >= k:
                break
    return out
