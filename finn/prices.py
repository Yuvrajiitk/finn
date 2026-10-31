"""End-of-day price/volume and the user-configurable 'unusual move' test."""
import math

def eod_stats(closes, volumes, lookback=20):
    """closes/volumes oldest->newest. Returns day change % and volume as a multiple of the prior-N-day average."""
    if len(closes) < 2 or len(volumes) < 2:
        return None
    prior = volumes[-lookback-1:-1]
    avg = sum(prior) / len(prior)
    chg = (closes[-1] / closes[-2] - 1) * 100
    if math.isnan(chg):
        return None
    return {"chg_pct": round(chg, 2),
            "vol_x": round(volumes[-1] / avg, 2) if avg else None, "close": closes[-1]}

def is_unusual(stats, px_pct=4.0, vol_x=2.0):
    if not stats: return []
    why = []
    if abs(stats["chg_pct"]) >= px_pct: why.append(f"price {stats['chg_pct']:+.1f}%")
    if stats["vol_x"] and stats["vol_x"] >= vol_x: why.append(f"volume {stats['vol_x']:.1f}x average")
    return why

def fetch_eod(tickers, suffix=".NS"):
    import yfinance as yf
    out = {}
    for t in tickers:
        h = yf.Ticker(t + suffix).history(period="2mo").dropna(subset=["Close", "Volume"])
        if h.empty and suffix == ".NS":  # fall back to BSE
            h = yf.Ticker(t + ".BO").history(period="2mo").dropna(subset=["Close", "Volume"])
        if not h.empty:
            s = eod_stats(h["Close"].tolist(), h["Volume"].tolist())
            if s:
                out[t] = s
    return out