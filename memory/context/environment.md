# 环境上下文

## 服务器
- **OpenClaw VPS**: root@23.95.34.155 (Debian 5.10, 1G RAM, 25G disk)
  - OpenClaw: v2026.2.24
  - Gateway: systemd user service, loopback-only, port 18789
- **FastGPT 服务器**: root@154.219.108.79 (Ubuntu 22.04, 4核/3.8G RAM)
  - FastGPT v4.13.1 (fastgpt.nianmo.top)
  - RedInk 红墨 (hm.nianmo.top, port 12398)
  - Caddy v2.11.1 反代, Cloudflare SSL (⚠️ 证书 2026-04-02 到期)
- **Hajimi VPS**: 同 OpenClaw VPS (23.95.34.155)
  - /opt/hajimi-king/repo, docker hajimi-king:0.0.1

## 模型 Provider
| Provider | 地址 | 主要模型 | 备注 |
|----------|------|---------|------|
| 003636 | api.003636.xyz/v1 | gpt-5.2-codex (默认), gpt-5.3-codex, gpt-5.2 | 主力 |
| anyrouter | anyrouter.top | claude-opus-4-6 | 群聊用, 偶尔不稳定 |
| gpt-load | load.201452.xyz/proxy/openai/v1 | GPT 全系 25+ 模型, DALL-E 3, TTS | key 池轮转偶尔抽风 |
| gemini2api | ge.320732.de5.net/v1 | gemini-auto/2.5-flash/2.5-pro/3-flash/3-pro/3.1-pro | 无 imagen |
| openai-custom | api.003636.xyz/v1 | 杂项转发模型 | monica/nebius/ohmygpt 子路由 |
| anthropic-custom | api.003636.xyz/v1 | claude-opus-4-5 | 备用 |
| dkjsiogu | api.dkjsiogu.me | claude-opus-4-6 | 路由固定到4.6, 偶发529 Overloaded |
| yuanjing | maas-api.ai-yuanjing.com/openapi/compatible-mode/v1 | glm-5, deepseek-r1/v3, qwen-plus/max | 试用限流~5RPM |
| apitest | openai.api-test.us.ci/v1 | deepseek-chat 等7个DeepSeek模型 | 实测OK |
| freestyle | 127.0.0.1:19090/v1 (本地代理) | claude-opus-4-6 | 上游直连被403, 需代理清洗请求头 |

## Alias
- sonnet → 003636/gpt-5.2-codex
- opus → 003636/gpt-5.3-codex
- haiku → openai-custom/gemini-2.5-flash
- dschat → apitest/deepseek-chat
- dsr1 → apitest/deepseek-reasoner
- f-opus → freestyle/claude-opus-4-6

## 搜索能力
| 源 | 状态 | 备注 |
|----|------|------|
| Tavily | ✅ | skill env, tp.aillm.cc.cd |
| Exa | ✅ | TOOLS.md |
| Grok | ✅ | api.003636.xyz, grok-4.1 |
| MinerU | ✅ | skill .env |
| SearXNG | ✅ | localhost:8888 |
| Brave | ❌ | 不使用 |

## 本地代理服务
| 端口 | 用途 | 脚本 | systemd |
|------|------|------|---------|
| 19090 | freestyle 请求头清洗 | scripts/freestyle_proxy.py | freestyle-proxy.service |
| 19091 | cliproxy 请求头清洗 | scripts/cliproxy_proxy.py | cliproxy-proxy.service |

## 其他服务
- 小红书 MCP: localhost:18060, 已登录
- GitHub CLI: gh, 账号 Bei0jnthmmq2yh4Quinn
- Twitter/X: bird v0.8.0, 已登录 @Nian_Mo_
- Grok2API: grok2api.xqp-grok.workers.dev (CF Workers, D1+KV)
