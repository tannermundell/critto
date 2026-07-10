"""
Critto — knowledge agent for the /entry endpoint.

Given a confirmed species it:
  1. Retrieves grounding text from Wikipedia (real facts, no key needed).
  2. If an LLM is configured, has it write the structured field-guide fields
     grounded ONLY in that text. Otherwise returns an honest grounded fallback
     (the real Wikipedia summary + "Not documented" for the split fields).

LLM is OpenAI-compatible, so the SAME code works with OpenAI now and Fireworks
at kickoff — you only change env vars:

  Local / OpenAI:   LLM_API_KEY=sk-...          (LLM_BASE_URL defaults to OpenAI)
  Fireworks:        LLM_BASE_URL=https://api.fireworks.ai/inference/v1
                    LLM_MODEL=accounts/fireworks/models/<model>
                    LLM_API_KEY=<fireworks key>

Results are cached in-memory per species to avoid repeat calls (and, later, to
conserve Fireworks credits).
"""

import json
import os
from typing import Optional

import requests

WIKI_API = "https://en.wikipedia.org/w/api.php"
LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "https://api.openai.com/v1").rstrip("/")
LLM_API_KEY = os.environ.get("LLM_API_KEY", "")
LLM_MODEL = os.environ.get("LLM_MODEL", "gpt-4o-mini")

FIELDS = ["habitat", "diet", "size", "range", "where_to_spot", "fun_fact"]

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "Critto-agent/1.0 (hackathon)"})

_CACHE: dict = {}


# --------------------------------------------------------------------------
# Retrieval
# --------------------------------------------------------------------------
def _wiki_extract(title: str) -> Optional[dict]:
    params = {
        "action": "query", "prop": "extracts", "explaintext": 1,
        "redirects": 1, "format": "json", "titles": title,
    }
    try:
        data = SESSION.get(WIKI_API, params=params, timeout=20).json()
    except Exception:
        return None
    for _, page in data.get("query", {}).get("pages", {}).items():
        if "missing" in page:
            continue
        extract = (page.get("extract") or "").strip()
        if extract:
            pageid = page.get("pageid")
            url = f"https://en.wikipedia.org/?curid={pageid}" if pageid else ""
            return {"title": page.get("title", title), "extract": extract, "url": url}
    return None


def retrieve_wikipedia(common: str, scientific: str) -> Optional[dict]:
    """Try the scientific name first (redirects resolve to the main article),
    then the common name."""
    for title in (scientific, common):
        if title:
            res = _wiki_extract(title)
            if res:
                return res
    return None


# --------------------------------------------------------------------------
# LLM synthesis (OpenAI-compatible; also works with Fireworks)
# --------------------------------------------------------------------------
def _extract_json(text: str) -> Optional[dict]:
    """Parse JSON, falling back to the outermost {...} if the model added prose."""
    try:
        return json.loads(text)
    except Exception:
        pass
    i, j = text.find("{"), text.rfind("}")
    if i != -1 and j > i:
        try:
            return json.loads(text[i:j + 1])
        except Exception:
            return None
    return None


def _chat(payload: dict) -> str:
    r = SESSION.post(
        f"{LLM_BASE_URL}/chat/completions",
        headers={"Authorization": f"Bearer {LLM_API_KEY}"},
        json=payload, timeout=60,
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


def _llm_fields(common: str, scientific: str, klass: str, reference: str) -> Optional[dict]:
    if not LLM_API_KEY:
        return None
    system = (
        "You are a wildlife field-guide writer. Using ONLY the reference text, fill "
        "each field in 1-2 concise, factual sentences. If a fact is not in the text, "
        "write 'Not documented'. Each field must contain DISTINCT information — never "
        "repeat the same fact in more than one field. The user separately sees an 'About' "
        "summary taken from the START of the reference text, so for 'fun_fact' give a "
        "genuinely surprising, lesser-known detail that is NOT the species' most obvious or "
        "defining feature and does NOT restate anything from the opening of the reference. "
        "Return ONLY a JSON object with exactly these keys: " + ", ".join(FIELDS) + "."
    )
    user = (
        f"Species: {common} ({scientific}), class {klass}.\n\n"
        f"Reference text:\n{reference}"
    )
    base = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0.3,
    }
    # Try strict JSON mode first, then without it (not every model supports
    # response_format), parsing leniently either way.
    for extra in ({"response_format": {"type": "json_object"}}, {}):
        try:
            content = _chat({**base, **extra})
        except Exception:
            continue
        data = _extract_json(content)
        if data:
            return {k: str(data.get(k, "")).strip() or "Not documented" for k in FIELDS}
    return None


# --------------------------------------------------------------------------
# Orchestration
# --------------------------------------------------------------------------
def build_entry(common: str, scientific: str, klass: str) -> dict:
    key = scientific or common
    if key in _CACHE:
        return _CACHE[key]

    wiki = retrieve_wikipedia(common, scientific)
    sources = []
    reference = ""
    summary = ""
    if wiki:
        reference = wiki["extract"][:5000]
        summary = wiki["extract"].split("\n")[0][:600]
        if wiki["url"]:
            sources.append(wiki["url"])

    fields = _llm_fields(common, scientific, klass, reference) if reference else None
    if fields is not None:
        model_version = "agent-llm"
    else:
        # Grounded fallback: keep the real Wikipedia summary; be honest about the
        # split fields until an LLM is connected.
        note = "Connect the language model for a detailed write-up." if reference \
            else "No reference text found for this species."
        fields = {f: ("Not documented" if reference else note) for f in FIELDS}
        model_version = "agent-fallback"

    result = {
        "summary": summary or "No summary available.",
        **fields,
        "sources": sources or ["none"],
        "model_version": model_version,
    }
    _CACHE[key] = result
    return result
