# MEMORY.md — 热缓存层

> 速查表，覆盖 90% 日常解码。深度信息查 memory/ 子目录。
> 
> 架构：热缓存 (MEMORY.md) → 深度存储 (memory/**/*.md)
> 查找路径 A（确定性）：热缓存 → glossary → 档案
> 查找路径 B（语义）：memory_search → memory_get

## 人物速查
- **老板 / xqp** — Telegram @nianmo173, EST 时区, 做小红书代运营, 偏好稳定不折腾

## 项目速查（主线）
- **捻墨运营笔记** — 小红书账号，个人接代运营，3000/月，2408粉
- 主线任务：帮老板管好这个账号的内容产出
- 内容策略：7:3（案例接单帖70% + 行业观点30%），禁纯干货教程
- 风格档案：`memory/writing-style.md`
- 内容管线：`memory/projects/nianmo-xhs.md`

## 偏好与协议
- 沟通直接，不喜欢废话
- **输出笔记时：一篇一条消息发给老板（不要一股脑连发），方便复制**
- **发 key 时：一条消息、纯密钥、每行一个、不带任何文字。先存着，不用每个都发，老板要的时候再发**
- 不存储/追踪媒体文件
- 不在聊天里处理密码
- 长期记忆尽量多存有用上下文

## 环境速查
- 默认模型：openai-codex/gpt-5.2-codex (003636)，也有 gpt-5.3-codex
- provider 改名 openai-custom→openai-codex 是为了支持 xhigh thinking
- 备用模型：anyrouter/claude-opus-4-6
- 搜索：Tavily ✅ (tp.aillm.cc.cd) / Exa ✅ / Grok ✅ / MinerU ✅ / SearXNG ✅ / Brave ❌（不使用）
- 搜索策略：默认走 search-layer + SearXNG，不用 Brave/web_search
- 小红书 MCP：localhost:18060 ✅
- Twitter/X：bird v0.8.0, @Nian_Mo_ ✅
- 详情 → `memory/context/environment.md`

## Hajimi King 速查
- **VPS**: root@23.95.34.155, /opt/hajimi-king/repo
- **容器**: hajimi-king:0.0.1, 8 进程, docker-compose
- **13 种 key**: gemini, openai, anthropic, groq, openrouter, deepseek, fireworks, together, hf_token, replicate, cohere, perplexity, zhipu
- **搜索**: 144 条 query, 三向搜索, SHA 去重
- **验证**: valid/429/invalid 三分管理, 每 1h 复验
- 详情 → `memory/2026-02-22.md`（部署记录）

## 深度存储索引
| 文件 | 内容 |
|------|------|
| `memory/glossary.md` | 缩写/代号/术语解码器 |
| `memory/post-mortems.md` | 经验教训 |
| `memory/projects/nianmo-xhs.md` | 捻墨项目详情 |
| `memory/context/environment.md` | 部署/工具栈/API 配置 |
| `memory/people/` | 人物档案（待补充） |
| `memory/knowledge/` | 可复用知识（待补充） |

## 维护规则
- 高频条目（周 3 次+）晋升到此文件
- 30 天未用条目降级回深度存储
- heartbeat 定期巡检
