"""Pull side. Primary sources only: screener.in tables + concall transcripts. No news, no broker notes.
Pipeline: (1) cheap model extracts explicit guidance per transcript, (2) code drops any quote not found verbatim in the
transcript, (3) one strong-model call compares promised vs delivered using only the supplied text and numbers."""
import requests
from bs4 import BeautifulSoup
from .llm import ask_json, CHEAP, STRONG
from .results import pdf_text
UA = {"User-Agent": "Mozilla/5.0"}

def page(ticker):
    for path in ("consolidated/", ""):
        r = requests.get(f"https://www.screener.in/company/{ticker}/{path}", headers=UA, timeout=20)
        if r.ok: return BeautifulSoup(r.text, "html.parser")
    raise ValueError(f"screener.in has no page for {ticker}")

def table(soup, section_id):
    t = soup.select_one(f"section#{section_id} table")
    if not t: return {}
    cols = [th.get_text(strip=True) for th in t.select("thead th")][1:]
    return {tr.select_one("td").get_text(strip=True).rstrip("+ ").strip():
            [td.get_text(strip=True).replace(",", "") for td in tr.select("td")[1:]]
            for tr in t.select("tbody tr") if tr.select_one("td")} | {"_cols": cols}

def transcripts(soup, n=4):
    links = [a["href"] for a in soup.select("section#documents a") if "transcript" in a.get_text().lower()]
    return links[:n]

GSYS = ("From this earnings-call transcript, list ONLY explicit forward-looking statements about headline numbers "
        "(revenue/volume growth, margins, capex, debt). JSON: {\"period\":\"e.g. Q2 FY27 call\",\"guidance\":"
        "[{\"metric\":str,\"target\":str,\"quote\":\"exact sentence copied from the text\"}]}. Empty list if none. No inference.")

def guidance(url):
    text = pdf_text(url, 60000)
    g = ask_json(CHEAP, GSYS, text, 1200)
    g["guidance"] = [x for x in g.get("guidance", []) if x.get("quote", "")[:80] in text]  # anti-hallucination gate
    return g

VSYS = ("You are a skeptical buy-side analyst. Using ONLY the guidance and the reported numbers given, judge each guidance item "
        "against what was delivered in the following quarters. JSON: {\"items\":[{\"call\":str,\"promise\":str,\"delivered\":str,"
        "\"verdict\":\"met|partly|missed|unclear\",\"note\":\"one line\"}],\"read\":\"2 sentences on whether tone and numbers agree\"}. "
        "Say 'unclear' rather than guess. Do not use outside knowledge of the company.")

def research(ticker):
    soup = page(ticker)
    actuals = {"quarters": table(soup, "quarters"), "years": table(soup, "profit-loss"), "balance": table(soup, "balance-sheet"),
               "cashflow": table(soup, "cash-flow"), "ratios": table(soup, "ratios")}
    g = [guidance(u) for u in transcripts(soup)]
    verdict = ask_json(STRONG, VSYS, f"GUIDANCE:\n{g}\n\nREPORTED (screener.in):\n{actuals['quarters']}", 2500)
    return {"ticker": ticker, "guidance": g, "promised_vs_delivered": verdict, "actuals": actuals}
