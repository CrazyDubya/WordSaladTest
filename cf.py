"""Cloudflare Workers AI text-generation client.

One function, `run()`, that POSTs to /ai/run/{model}, pulls text out of
result.response, backs off on 429/5xx, and raises ScopeError when the token
can't reach Workers AI. Throttled to ~5 req/s so a full run stays under the
per-model rate limit.
"""
import os
import time

import requests

ACCOUNT_ID = os.environ.get("CF_ACCOUNT_ID")
TOKEN = os.environ.get("CF_API_TOKEN")

MIN_INTERVAL = 0.2  # seconds between requests -> ~5 req/s, well under 300/min
_last = [0.0]


class ScopeError(RuntimeError):
    """Token is invalid or lacks the Workers AI permission."""


def _throttle():
    wait = MIN_INTERVAL - (time.time() - _last[0])
    if wait > 0:
        time.sleep(wait)
    _last[0] = time.time()


def run(model, messages, max_tokens=8, temperature=0.0, seed=42, retries=6):
    """Call a Workers AI model and return the generated text (str)."""
    if not TOKEN:
        raise RuntimeError("CF_API_TOKEN not set in environment")
    if not ACCOUNT_ID:
        raise RuntimeError("CF_ACCOUNT_ID not set in environment")
    url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/run/{model}"
    body = {
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "seed": seed,
    }
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    delay = 1.0
    for _ in range(retries):
        _throttle()
        try:
            r = requests.post(url, headers=headers, json=body, timeout=90)
        except requests.RequestException:
            time.sleep(delay)
            delay = min(delay * 2, 30)
            continue
        if r.status_code == 200:
            data = r.json()
            if data.get("success"):
                return data["result"]["response"]
            raise RuntimeError(f"{model}: {data.get('errors')}")
        if r.status_code in (401, 403):
            raise ScopeError(f"HTTP {r.status_code} for {model}: {r.text[:200]}")
        if r.status_code == 429 or r.status_code >= 500:
            time.sleep(delay)
            delay = min(delay * 2, 30)
            continue
        raise RuntimeError(f"{model} HTTP {r.status_code}: {r.text[:200]}")
    raise RuntimeError(f"{model}: exhausted {retries} retries")
