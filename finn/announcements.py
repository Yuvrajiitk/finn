"""NSE corporate announcements. NSE needs a browser-like session (cookie from the homepage first)."""
import datetime as dt, requests
from .classify import classify
H = {"User-Agent": "Mozilla/5.0", "Accept": "application/json", "Referer": "https://www.nseindia.com/"}

def _session():
    s = requests.Session(); s.headers.update(H)
    s.get("https://www.nseindia.com", timeout=15)  # warm-up for cookies
    return s

def fetch(symbol, hours=24, s=None):
    s = s or _session()
    r = s.get("https://www.nseindia.com/api/corporate-announcements",
              params={"index": "equities", "symbol": symbol}, timeout=15)
    r.raise_for_status()
    cutoff = dt.datetime.now() - dt.timedelta(hours=hours)
    out = []
    for a in r.json():
        when = dt.datetime.strptime(a["an_dt"], "%d-%b-%Y %H:%M:%S")
        if when < cutoff: continue
        cat, pri = classify(a.get("desc", ""), a.get("attchmntText", ""))
        out.append({"symbol": symbol, "when": when.isoformat(), "category": cat, "priority": pri,
                    "title": a.get("desc"), "text": a.get("attchmntText"), "file": a.get("attchmntFile")})
    return sorted(out, key=lambda x: (-x["priority"], x["when"]), reverse=False)

def digest(symbols, hours=24):
    s = _session(); items = []
    for sym in symbols:
        try: items += fetch(sym, hours, s)
        except Exception as e: items.append({"symbol": sym, "error": str(e), "priority": 0})
    seen = set(); uniq = []
    for i in items:
        k = (i.get("symbol"), i.get("title"), i.get("text"))
        if k in seen: continue
        seen.add(k); uniq.append(i)
    items = uniq
    shown = [i for i in items if i.get("priority", 0) > 1]
    return {"total": len(items), "matter": len(shown), "items": sorted(shown, key=lambda i: -i["priority"]),
            "routine_hidden": len(items) - len(shown)}
