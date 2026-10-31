"""Thin LLM wrapper: disk cache + two model tiers. Cheap model for bulk extraction, strong model only for judgement."""
import hashlib, json, os, pathlib, re
CHEAP = os.getenv("FINN_CHEAP_MODEL", "claude-haiku-5-5")
STRONG = os.getenv("FINN_STRONG_MODEL", "claude-sonnet-5-5")
CACHE = pathlib.Path(os.getenv("FINN_CACHE", ".cache/llm")); CACHE.mkdir(parents=True, exist_ok=True)

def ask(model, system, user, max_tokens=1500):
    key = hashlib.sha256(json.dumps([model, system, user]).encode()).hexdigest()
    f = CACHE / key
    if f.exists():
        return f.read_text()
    import anthropic  # imported lazily so tests run without a key
    r = anthropic.Anthropic().messages.create(model=model, max_tokens=max_tokens, system=system,
                                              messages=[{"role": "user", "content": user}])
    out = r.content[0].text
    f.write_text(out)
    return out

def ask_json(model, system, user, max_tokens=1500):
    raw = ask(model, system + "\nReply with JSON only, no prose, no code fences.", user, max_tokens)
    return json.loads(re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.M).strip())
