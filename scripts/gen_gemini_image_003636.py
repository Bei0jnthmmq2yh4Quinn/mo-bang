#!/usr/bin/env python3
"""Generate an image via 003636 (openai-compatible) Gemini image model.

Why this exists
- 003636 exposes Gemini image generation in /v1/chat/completions as `message.images[*].image_url.url`
  (data URL with base64). The /v1/responses path may return no image blocks.

Usage
  python3 scripts/gen_gemini_image_003636.py \
    --prompt "a red circle on white background" \
    --out outputs/test.png \
    --model gemini-3-pro-image

Notes
- Uses the `openai-custom` provider key + baseUrl from /root/.openclaw/openclaw.json.
- Does NOT print the full base64 to stdout.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
from pathlib import Path

import requests


def load_003636_openai_custom() -> tuple[str, str]:
    cfg_path = Path("/root/.openclaw/openclaw.json")
    cfg = json.loads(cfg_path.read_text("utf-8"))
    prov = cfg["models"]["providers"]["openai-custom"]
    return prov["baseUrl"].rstrip("/"), prov["apiKey"]


def extract_data_url_image(payload: dict) -> str:
    """Return data url like data:image/jpeg;base64,... from various 003636 schemas."""

    def looks_like_data_url(s: str) -> bool:
        return isinstance(s, str) and s.startswith("data:image/") and ";base64," in s

    try:
        # Schema A: chat.completions with message.images
        if isinstance(payload, dict) and "choices" in payload:
            choice0 = (payload.get("choices") or [None])[0] or {}
            msg = choice0.get("message") or {}

            images = msg.get("images") or []
            if images:
                url = (images[0].get("image_url") or {}).get("url")
                if looks_like_data_url(url):
                    return url

            # Schema B: some providers embed a data URL in content text
            content = msg.get("content")
            if looks_like_data_url(content):
                return content
            if isinstance(content, str) and "data:image/" in content:
                # extract first data url substring
                idx = content.find("data:image/")
                return content[idx:].strip()

        # Schema C: OpenAI responses-like output blocks
        if isinstance(payload, dict) and "output" in payload:
            for out in payload.get("output") or []:
                for c in out.get("content") or []:
                    url = c.get("url") or c.get("image_url")
                    if looks_like_data_url(url):
                        return url

        raise KeyError("no data-url image found")
    except Exception as e:
        raise RuntimeError(
            f"Could not extract image from response. keys={list(payload.keys())}"
        ) from e


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default="gemini-3-pro-image")
    ap.add_argument(
        "--fallback-models",
        default="gemini-3-pro-high,gemini-3-flash",
        help="Comma-separated fallback models to try if primary fails",
    )
    ap.add_argument("--size", default=None, help="Optional hint in prompt only (e.g. 1080x1440 or 3:4)")
    ap.add_argument("--timeout", type=int, default=120)
    ap.add_argument("--retries", type=int, default=3, help="Retry on transient HTTP errors (e.g. 504)")
    ap.add_argument("--retry-backoff", type=float, default=1.8, help="Exponential backoff base")
    args = ap.parse_args()

    base_url, api_key = load_003636_openai_custom()

    prompt = args.prompt.strip()
    if args.size:
        prompt = f"Generate an image ({args.size}). {prompt}"

    import time

    fallback_models = [m.strip() for m in (args.fallback_models or "").split(",") if m.strip()]
    models_to_try = [args.model] + fallback_models

    last_err = None
    data_url = None
    used_model = None

    for model_id in models_to_try:
        body = {
            "model": model_id,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        }

        for attempt in range(args.retries + 1):
            try:
                r = requests.post(
                    f"{base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                    json=body,
                    timeout=args.timeout,
                )

                if r.status_code != 200:
                    # Retry only on likely-transient gateway/server errors.
                    if r.status_code in (429, 500, 502, 503, 504) and attempt < args.retries:
                        last_err = f"model={model_id} HTTP {r.status_code}: {r.text[:200]}"
                        time.sleep(args.retry_backoff ** attempt)
                        continue
                    # Non-retryable for this model; move to next model.
                    last_err = f"model={model_id} HTTP {r.status_code}: {r.text[:200]}"
                    break

                data = r.json()
                data_url = extract_data_url_image(data)
                used_model = model_id
                break
            except (requests.Timeout, requests.ConnectionError) as e:
                if attempt < args.retries:
                    last_err = f"model={model_id} {repr(e)}"
                    time.sleep(args.retry_backoff ** attempt)
                    continue
                last_err = f"model={model_id} {repr(e)}"
                break

        if data_url:
            break

    if not data_url:
        print(f"Failed after trying models {models_to_try}. Last error: {last_err}", file=sys.stderr)
        return 2
    header, b64 = data_url.split(",", 1)
    # content-type
    ext = "png"
    if header.startswith("data:image/jpeg"):
        ext = "jpg"
    elif header.startswith("data:image/png"):
        ext = "png"

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    # if user passed a path without extension, add one
    if out_path.suffix == "":
        out_path = out_path.with_suffix(f".{ext}")

    out_path.write_bytes(base64.b64decode(b64))
    print(f"Saved: {out_path}")
    if used_model:
        print(f"ModelUsed: {used_model}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
