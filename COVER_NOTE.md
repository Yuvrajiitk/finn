Subject: ENAM - IIT screening - 2027

Hi team,

Here is my submission for FINN.

Links
- Prototype (open on a phone): <PASTE PUBLISHED LINK>
- Repo: <PASTE GITHUB LINK>
- Build history: <PASTE CHAT EXPORT / SHARE LINKS>

What I built
FINN opens with one sentence: how many filings came in, and how many of them matter. The digest ranks by priority and folds the routine ones away. Results filings open into Revenue, EBITDA, PBT and PAT with QoQ and YoY. Alerts let you set what "unusual" means (price move, volume multiple, filing types). Research is built around promised-versus-delivered: management guidance from the last four calls, set against what the numbers did.

Key decisions
- Filtering is the product, so priority and the hidden-routine count are the first thing you see.
- Rules classify announcements; models are reserved for reading numbers and for judgement. All arithmetic is in code, not the model.
- A cheap model extracts guidance from each transcript; a stronger model is called once per company. Every guidance item has to carry a quote that exists in the transcript or it is dropped. Everything is cached.

What is and isn't real
The engine (NSE, yfinance, screener.in, extraction) is written, and its logic is unit-tested, but I have not yet run it against the live sites. The hosted prototype runs on clearly labelled sample data, so the numbers you see there are not real company figures. The management-change bio is a mock; LinkedIn enrichment is not built.

Left out deliberately
Auth, database, push delivery, OCR, balance-sheet and cash-quality views.

Next
Connect front-end to the API, schedule the digest and send web push, and add the cash-conversion and leverage panels.

Thanks,
<YOUR NAME>
