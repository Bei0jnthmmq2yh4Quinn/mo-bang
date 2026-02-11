# MEMORY.md - Long-term memory (curated)

> Curated, durable notes meant to survive across sessions.
> Avoid storing secrets (passwords, raw API keys). Store preferences, decisions, stable setup facts.

## User preferences & boundaries

- Prefer stability: do not break output or Telegram connectivity while doing maintenance.
- Do not send/handle passwords in chat; advise using password reset + 2FA if credentials were exposed.
- Long-term memory preference: **store as much useful context as possible**, but **do not store/track media files** (videos/images/attachments) in long-term memory.

## Environment / setup highlights

- OpenClaw gateway runs as a user systemd service (loopback-only).
- Control UI pairing has been used before; pairing approvals may be needed after token mismatch.

## Memory system decisions

- Tried enabling `memory-lancedb` as long-term memory backend; dependencies/version alignment were fixed, but user decided to stop using it and keep default `memory-core`.

## Models / workflow

- Default working model: `openai-custom/gpt-5.2`.
- Configured model providers (from local config):
  - `openai-custom` → baseUrl `https://api.003636.xyz/v1` → models: `gpt-5.2`
  - `anyrouter` → baseUrl `https://anyrouter.top` → models: `claude-opus-4-5-20251101`, `claude-opus-4-6`
- Agent model allowlist/shortcuts contains many additional model ids (81 entries) beyond provider-declared models; treat as “available to select if provider supports it”.

## Search

- `web_search` (Brave) is currently not configured (missing `BRAVE_API_KEY`).
- User recalls having set up search before; if web_search is needed again, either reconfigure Brave key or use browser/manual search.

## Ongoing project: XHS (RedNote) copywriting style learning from CSV

- Source CSV: `/root/.openclaw/media/inbound/file_24---7cad800e-9370-4fe0-a49f-e02823047e41.csv` ("捻墨运营笔记"-style notes)
- Parsed successfully with encoding `utf-8-sig`; schema: 笔记ID/笔记标题/笔记内容/点赞量/收藏量/评论量/分享量
- Actual record count: **303**
- Default combined performance score (user asked to "combine" signals): `score = like + 2*fav + 3*comment + 3*share` (tunable)
- Distribution highlights (mean/median/max): like 6.84/2/364; fav 4.13/1/266; comment 5.27/1/397; share 2.21/0/149; score 37.53/7/2501 (long-tail)
- Top-performing titles are dominated by pricing anchoring + anti-scam stance + boundaries (e.g., "3000/月" "无套路" "满意再继续" "不踩坑")
- Most frequent tags: #小红书企业号运营 #代运营 #笔记灵感 #小红书运营 #代运营服务 #捻墨运营笔记 #新媒体运营 #引流获客 #小红书代运营

## Assets / design work

- Created a Xiaohongshu cover background series for "self-media operations / knowledge content": two light electric-blue variants and one dark neon-green variant (generated via nano-banana-pro) and delivered via Telegram.

## nano-banana-pro / 003636 图片生成规则

- **nano-banana-pro 原脚本限制**：当设置了 `NANO_BANANA_BASE_URL`（如 003636）时，脚本禁止使用 `-i` 参考图参数。
- **绕过方案**：使用自定义脚本 `scripts/gen_xhs_cover_003636.py`，直接调用 003636 的 `/chat/completions` 接口，把参考图作为多模态 content（image_url + base64）发送。
- **接口格式**：
  - URL: `https://api.003636.xyz/v1/chat/completions`
  - Model: `gemini-3-pro-image`
  - Auth: `Authorization: Bearer <API_KEY>`（用现有 openai-custom 的 key）
  - 参考图传法：content 数组里加 `{"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}}`
  - 返回图片在：`choices[0].message.images[0].image_url.url`（data URL）
- **小红书封面常用 prompt 模板**（奶油白极简风）：竖版3:4、极简设计、奶油白/米白背景、浅粉色细线条几何装饰、大面积上方留白给标题、人物靠右下角、不要任何可读文字、添加细微噪点质感。
