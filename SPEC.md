# 墨榜 - 自媒体运营工具

## 项目简介
一款帮助自媒体创作者的工具，提供热点查询、对标分析、AI选题等功能。

## 功能列表

### 1. 热点查询
- 抖音热搜获取（网页公开接口）
- 小红书热门获取（探索页数据）

### 2. 对标分析
- 输入竞品账号，分析内容风格
- 数据概览

### 3. AI 生成选题
- 基于热点 + 对标分析
- AI 生成选题建议（结构化输出）

## 技术栈
- Python 3.10+
- FastAPI
- httpx (HTTP 请求)
- yt-dlp (视频下载)

## API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| /api/trends/douyin | GET | 获取抖音热搜 |
| /api/trends/xiaohongshu | GET | 获取小红书热门 |
| /api/analysis/benchmark | POST | 对标分析 |
| /api/topics/generate | POST | AI生成选题 |

## 运行方式
```
pip install -r requirements.txt
python main.py
```
