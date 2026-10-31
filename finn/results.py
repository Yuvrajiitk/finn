"""Results filing -> Revenue/EBITDA/PBT/PAT with QoQ and YoY. The LLM only *reads* numbers; all arithmetic is in code."""
import io, requests
from .llm import ask_json, CHEAP
SYS = ("You read an Indian quarterly results filing. Return the CONSOLIDATED figures if present, else standalone. "
       "Filings show three columns: quarter ended (current), preceding quarter, same quarter last year. "
       "Return JSON: {\"basis\":\"consolidated|standalone\",\"unit\":\"crore|lakh|million\","
       "\"revenue\":[cur,prev,yago],\"pbt\":[...],\"pat\":[...],\"finance_cost\":[...],\"depreciation\":[...],"
       "\"other_income\":[...],\"ebitda\":[...] or null if not reported}. Use null for anything not in the text. Never estimate.")

def pdf_text(url, max_chars=30000):
    from pypdf import PdfReader
    b = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30).content
    return "\n".join((p.extract_text() or "") for p in PdfReader(io.BytesIO(b)).pages[:12])[:max_chars]

def growth(cur, base):
    return None if cur is None or not base else round((cur / base - 1) * 100, 1)

def headline(d):
    # EBITDA, if not reported = PBT + finance cost + depreciation - other income (derived, and flagged as such)
    eb, derived = d.get("ebitda"), False
    if not eb and all(d.get(k) and None not in d[k] for k in ("pbt", "finance_cost", "depreciation", "other_income")):
        eb = [d["pbt"][i] + d["finance_cost"][i] + d["depreciation"][i] - d["other_income"][i] for i in range(3)]
        derived = True
    out = {}
    for k, v in (("revenue", d.get("revenue")), ("ebitda", eb), ("pbt", d.get("pbt")), ("pat", d.get("pat"))):
        if v and None not in v:
            out[k] = {"value": v[0], "qoq": growth(v[0], v[1]), "yoy": growth(v[0], v[2])}
    if derived and "ebitda" in out: out["ebitda"]["derived"] = True
    return {"unit": d.get("unit"), "basis": d.get("basis"), **out}

def from_filing(url):
    return headline(ask_json(CHEAP, SYS, pdf_text(url)))
