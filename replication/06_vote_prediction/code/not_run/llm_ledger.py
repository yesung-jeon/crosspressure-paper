"""Cached, logged LLM calls for API backends (principles C3, G4, R7, R12).

Every call is keyed by a hash of (provider, model, messages, parameters). A cached response is returned
without a new API call, so re-running an analysis does not change its inputs or cost. Each new call appends
one line to ledger.jsonl with time, model, parameters, prompt hash, response, token usage and latency.

Keys come from environment variables loaded from a .env file; never pass a key on the command line or store
it in code or settings (global safety rule, 2026-10-02 lesson). Sending prompts to an external API is an
outward-facing action: get the user's approval in the current session first.

Library use:
    from llm_ledger import Ledger
    L = Ledger("runs/ledger")                      # creates cache/ and ledger.jsonl
    text = L.chat("openai", "gpt-4.1-mini", [{"role": "user", "content": "..."}], temperature=0, max_tokens=50)

CLI summary of a ledger:
    python llm_ledger.py summary runs/ledger
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from pathlib import Path


def load_dotenv(path=".env"):
    p = Path(path)
    if not p.exists():
        return
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


class Ledger:
    def __init__(self, folder, dotenv=".env", max_retries=8, backoff=5.0):
        self.dir = Path(folder)
        (self.dir / "cache").mkdir(parents=True, exist_ok=True)
        self.ledger = self.dir / "ledger.jsonl"
        self.max_retries, self.backoff = max_retries, backoff
        load_dotenv(dotenv)

    def _key(self, provider, model, messages, params):
        blob = json.dumps({"p": provider, "m": model, "msg": messages, "params": params}, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()

    def chat(self, provider, model, messages, **params):
        key = self._key(provider, model, messages, params)
        cpath = self.dir / "cache" / f"{key}.json"
        if cpath.exists():
            return json.loads(cpath.read_text(encoding="utf-8"))["text"]
        t0 = time.time()
        for attempt in range(self.max_retries):
            try:
                text, usage = self._call(provider, model, messages, params)
                break
            except Exception as e:  # transient errors: retry with backoff (S01 Roper batch pattern)
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(self.backoff * (2 ** attempt))
        rec = {"time": time.strftime("%Y-%m-%dT%H:%M:%S"), "provider": provider, "model": model, "params": params,
               "prompt_sha256": key, "text": text, "usage": usage, "latency_s": round(time.time() - t0, 2)}
        cpath.write_text(json.dumps(rec, ensure_ascii=False), encoding="utf-8")
        with open(self.ledger, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        return text

    def _call(self, provider, model, messages, params):
        if provider in ("openai", "openai_compatible"):
            from openai import OpenAI

            client = OpenAI(base_url=params.pop("base_url", None), api_key=os.environ.get(params.pop("api_key_env", "OPENAI_API_KEY")))
            r = client.chat.completions.create(model=model, messages=messages, **params)
            u = r.usage
            return r.choices[0].message.content or "", ({"in": u.prompt_tokens, "out": u.completion_tokens} if u else None)
        if provider == "anthropic":
            import anthropic

            client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
            system = next((m["content"] for m in messages if m["role"] == "system"), None)
            msgs = [m for m in messages if m["role"] != "system"]
            kw = dict(model=model, messages=msgs, max_tokens=params.pop("max_tokens", 512), **params)
            if system:
                kw["system"] = system
            r = client.messages.create(**kw)
            return "".join(b.text for b in r.content if getattr(b, "type", "") == "text"), {"in": r.usage.input_tokens, "out": r.usage.output_tokens}
        raise ValueError(f"unknown provider {provider}")


def summary(folder):
    p = Path(folder) / "ledger.jsonl"
    rows = [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()] if p.exists() else []
    by = {}
    for r in rows:
        k = (r["provider"], r["model"])
        d = by.setdefault(k, {"calls": 0, "in": 0, "out": 0})
        d["calls"] += 1
        if r.get("usage"):
            d["in"] += r["usage"].get("in") or 0
            d["out"] += r["usage"].get("out") or 0
    return {f"{k[0]}:{k[1]}": v for k, v in by.items()}


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["summary"])
    ap.add_argument("folder")
    a = ap.parse_args()
    print(json.dumps(summary(a.folder), indent=1))
