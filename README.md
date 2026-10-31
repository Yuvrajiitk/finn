# FINN

A phone-first investor assistant that is built around one idea: the product is the filter, not the feed.

- `web/index.html` – the mobile front-end (single file, no build step). Runs on sample data so it can be tried anywhere.
- `finn/` – the engine. `classify` (rules), `prices` (EOD + spike test), `announcements` (NSE), `results` (filing to headline numbers), `research` (screener.in + concalls).
- `app.py` – FastAPI wrapper: `/digest`, `/alerts/eod`, `/results?url=`, `/research/{ticker}`.

## Run
    pip install -r requirements.txt
    export ANTHROPIC_API_KEY=...        # only needed for /results and /research
    pytest                               # offline tests: classifier, spike logic, QoQ/YoY maths
    uvicorn app:app --reload

## Status (honest)
Tested offline: classifier, spike detector, growth/EBITDA maths (`pytest`).
Written but not yet run against live sites: NSE fetch, yfinance fetch, screener.in parsing, both LLM steps. NSE and screener change markup and
block bots, so expect to adjust selectors on first run. The front-end currently reads sample data, not these endpoints.

## Decisions
1. **Rules before models.** Announcement types are mostly keyword-decidable. Rules are free, instant and debuggable. An LLM would only see what rules call `unclassified`.
2. **Models read, code calculates.** The LLM pulls raw numbers out of the filing; QoQ/YoY, margins and derived EBITDA are computed in code. If a filing has no EBITDA line it is derived (PBT + finance cost + depreciation - other income) and flagged `derived`.
3. **Two model tiers.** Cheap model for per-transcript extraction (bulk, 4+ calls per ticker). Strong model once per ticker for the promised-vs-delivered judgement.
4. **Guidance must be quotable.** Every extracted guidance item carries a verbatim quote; items whose quote is not found in the transcript text are dropped. This is the main guard against invented guidance.
5. **Cache everything by content hash** (`.cache/llm`). Re-opening a company costs nothing.
6. **Primary sources only on Pull.** Screener tables + transcripts; no news or broker data.

## Left out on purpose
Auth, a database, scheduling/push delivery (the alerts logic is there, the delivery channel is not), LinkedIn enrichment for management changes (profile card is a mock), scanned-PDF OCR, balance-sheet and cash-quality views.

## Next
Wire the front-end to the API; a scheduler plus web push; per-user thresholds in a store; cash-conversion and leverage panels from the tables already fetched.
