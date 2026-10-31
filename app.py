"""uvicorn app:app --reload   (ANTHROPIC_API_KEY needed only for /results and /research)"""
import json
from fastapi import FastAPI
from finn import announcements, prices, results, research
P = json.load(open("portfolio.json"))
app = FastAPI(title="FINN")

@app.get("/digest")
def digest(hours: int = 24): return announcements.digest(P["portfolio"], hours)

@app.get("/alerts/eod")
def eod(px: float = 4.0, vol: float = 2.0):
    s = prices.fetch_eod(P["portfolio"])
    return [{"symbol": k, **v, "why": prices.is_unusual(v, px, vol)} for k, v in s.items() if prices.is_unusual(v, px, vol)]

@app.get("/results")
def res(url: str): return results.from_filing(url)

@app.get("/research/{ticker}")
def rs(ticker: str): return research.research(ticker.upper())
