# MEMORY.md — Long-term memory (curated)

> Curated, durable notes meant to survive across sessions.
> Avoid storing secrets (passwords, raw API keys). Store preferences, decisions, stable setup facts.

## User preferences & boundaries

- Prefer stability: do not break output or Telegram connectivity while doing maintenance.
- Do not send/handle passwords in chat; advise using password reset + 2FA if credentials were exposed.

## Environment / setup highlights

- OpenClaw gateway runs as a user systemd service (loopback-only).
- Control UI pairing has been used before; pairing approvals may be needed after token mismatch.

## Memory system decisions

- Tried enabling `memory-lancedb` as long-term memory backend; dependencies/version alignment were fixed, but user decided to stop using it and keep default `memory-core`.

## Models / workflow

- Model has been switched before (gemini preview ↔ gpt-5.2) with gateway restarts; default working model is `openai-custom/gpt-5.2`.

## Search

- `web_search` (Brave) is currently not configured (missing `BRAVE_API_KEY`).
- User recalls having set up search before; if web_search is needed again, either reconfigure Brave key or use browser/manual search.

## Assets / design work

- Created a Xiaohongshu cover background series for “self-media operations / knowledge content”: two light electric-blue variants and one dark neon-green variant (generated via nano-banana-pro) and delivered via Telegram.
