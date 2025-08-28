from helpers.product_grouping import _base_name

def finalize_recommendations(parsed, shortlist, k):
    # Build allowlists from shortlist
    id_to_name = {}
    allowed_ids = set()
    for p in shortlist:
        pid = str(p.metadata.get("product_id") or p.id or "").strip()
        if not pid:
            continue
        allowed_ids.add(pid)
        id_to_name[pid] = (p.name or "").strip()

    out, seen = [], set()
    for r in parsed.recommendations:
        pid = str(getattr(r, "product_id", "")).strip()
        pname = (getattr(r, "product_name", "") or "").strip()
        if not pid or pid not in allowed_ids:
            continue  # drop invented/invalid IDs
        # name must be consistent with shortlist (base-name tolerant)
        bn_model = _base_name(pname).lower()
        bn_short = _base_name(id_to_name.get(pid, "")).lower()
        if bn_model and bn_short and bn_model != bn_short:
            continue  # ID↔name mismatch, drop
        if pid in seen:
            continue  # dedupe by product_id
        seen.add(pid)
        out.append(r)
        if len(out) >= k:
            break
    parsed.recommendations = out
    return parsed
