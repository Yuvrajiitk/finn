# FINN

A phone-first investor assistant built around one idea: the product is the filter, not the feed.

**Live demo (open on a phone):** https://mellifluous-peony-9df1d3.netlify.app

## What's here

- `web/index.html` – the mobile front-end (single file, no build step). Digest and Alerts show a snapshot of live data taken on 31 Oct 2026; the Research tab still uses illustrative figures.
- `finn/` – the engine: `classify` (rules), `prices` (end-of-day and spike test), `announcements` (NSE), `results` (filing to headline numbers), `research` (screener.in and concalls), `llm` (model tiers and cache).
- `app.py` – FastAPI wrapper: `/digest`, `/alerts/eod`, `/results?url=`, `/research/{ticker}`.
- `eod_snapshot.json`, `digest_snapshot.json` – saved output of the two live endpoints. The hosted front-end is built from these.
- `tests/` – offline tests for the classifier, spike detector and growth maths.

## Run it

```
pip install -r requirements.txt
python -m pytest
uvicorn app:app --reload
```

Then open http://127.0.0.1:8000/docs to try the endpoints. `/results` and `/research` also need an `ANTHROPIC_API_KEY` set in the terminal.

## Status

**Working against live sources:** the yfinance end-of-day fetch with spike detection (`/alerts/eod`) and the NSE announcements fetch with classification (`/digest`).

**Tested offline:** classifier, spike detector, growth and EBITDA maths.

**Written but not run yet:** results extraction from filing PDFs (`/results`), and screener.in parsing plus the research step (`/research`). Both need an LLM key. The Research tab in the front-end shows illustrative figures, not real extractions.

**Known issue:** the classifier takes the first keyword match, so a dividend notice that also mentions results gets labelled "results". Planned fix: use NSE's own subject line first, keywords second.

## Decisions

1. **Rules before models.** Announcement types are mostly keyword-decidable. Rules are free, instant and easy to debug. An LLM would only see what the rules call `unclassified`.
2. **Models read, code calculates.** The LLM pulls raw numbers out of a filing. QoQ, YoY, margins and derived EBITDA are computed in code. If a filing has no EBITDA line, it is derived (PBT + finance cost + depreciation - other income) and flagged `derived`.
3. **Two model tiers.** A cheap model for per-transcript extraction (bulk, several calls per ticker). A stronger model once per ticker for the promised-versus-delivered judgement.
4. **Guidance must be quotable.** Every extracted guidance item carries a verbatim quote. Items whose quote is not found in the transcript text are dropped, as a guard against invented guidance.
5. **Cache everything by content hash** (`.cache/llm`), so reopening a company costs nothing.
6. **Primary sources only on the research side.** Screener tables and transcripts; no news or broker data.
7. **Duplicates removed in the digest.** The same filing often arrives more than once, so it is deduplicated before counting what matters.

## Left out on purpose

Auth, a database, scheduling and push delivery (the alert logic is there, the delivery channel is not), LinkedIn enrichment for management changes (the filing text rarely names the person), scanned-PDF OCR, and balance-sheet and cash-quality views.

## Next

Wire the front-end to the API instead of snapshots, fix the classifier ordering, run `/results` on real filings so results cards show Revenue, EBITDA, PBT and PAT, add a scheduler with web push, and store per-user thresholds.
