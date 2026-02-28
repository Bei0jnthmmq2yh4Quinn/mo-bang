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

## 模型切换别名
| 输入 | 实际模型 |
|------|----------|
| `52` | 003636/gpt-5.2-codex（默认） |
| `53` | 003636/gpt-5.3-codex |
| `think` | cliproxy/claude-opus-4-6-thinking |
| `haiku` | openai-custom/gemini-2.5-flash |
| `f-opus` | freestyle/claude-opus-4-6 |
| `dschat` | apitest/deepseek-chat |
| `dsr1` | apitest/deepseek-reasoner |
- 用法：`/model 别名` 切换，`/model default` 切回

## 偏好与协议
- 沟通直接，不喜欢废话
- **输出笔记时：一篇一条消息发给老板（不要一股脑连发），方便复制**
- **发 key 时：一条消息、纯密钥、每行一个、不带任何文字。先存着，不用每个都发，老板要的时候再发**
- 不存储/追踪媒体文件
- 不在聊天里处理密码
- 长期记忆尽量多存有用上下文

## 环境速查
- 默认模型：003636/gpt-5.2-codex，也有 gpt-5.3-codex（alias: opus）
- 备用模型：anyrouter/claude-opus-4-6（群聊用）
- 其他渠道：gpt-load（25+ 模型）、gemini2api（6 模型）、openai-custom（杂项转发）
- 搜索：Tavily ✅ / Exa ✅ / Grok ✅ / MinerU ✅ / SearXNG ✅ / Brave ❌
- 搜索策略：默认走 search-layer + SearXNG，不用 Brave/web_search
- 小红书 MCP：localhost:18060 ✅
- Twitter/X：bird v0.8.0, @Nian_Mo_ ✅
- Grok2API：grok2api.xqp-grok.workers.dev（CF Workers）
- FastGPT：fastgpt.nianmo.top / RedInk：hm.nianmo.top
- ⚠️ SSL 证书 2026-04-02 到期（FastGPT 服务器 Cloudflare origin cert）
- 详情 → `memory/context/environment.md`

## Hajimi King 速查
- **VPS**: root@23.95.34.155, /opt/hajimi-king/repo
- **容器**: hajimi-king:0.0.1, 8 进程, docker-compose
- **13 种 key**: gemini, openai, anthropic, groq, openrouter, deepseek, fireworks, together, hf_token, replicate, cohere, perplexity, zhipu
- **搜索**: 272 条 query, 三向搜索, SHA 去重, 19000+ SHA 已扫
- **验证**: valid/429/invalid 三分管理, 每 1h 复验
- **现状**: GitHub 公开 key 红利期已过，有效产出递减
- 详情 → `memory/2026-02-22.md`（部署记录）

## Skills 工具箱（自媒体相关）
| Skill | 用途 | 触发场景 |
|-------|------|---------|
| **xiaohongshu-mcp** | 小红书数据拉取+发布 | 查账号数据、发笔记 |
| **xiaohongshu-title** | 批量生成小红书标题 | 选题/起标题时 |
| **douyin-hot-trend** | 抖音热搜趋势 | 找选题灵感、蹭热点 |
| **content-repurposing-engine** | 内容二次创作 | 一篇改多平台版本 |
| **nano-banana-pro** | AI 图片/封面生成 | 做封面、配图 |
| **video-frames** | 视频抽帧看内容 | 老板发抖音链接时 |
| **yt-dlp**（命令行） | 下载抖音/YouTube 视频 | 配合 video-frames |

## 新 VPS（23.80.89.41）
- **用途**: 客户部署 OpenClaw（C 方案）
- **系统**: Debian 12, 6G RAM, 99G disk
- **已装**: Node 22 + pnpm + OpenClaw 2026.2.26 + systemd 服务
- **已有服务**: CLIProxy + Caddy（fzl.201452.xyz）
- **待办**: 等老板给 Telegram bot token + 模型配置

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
