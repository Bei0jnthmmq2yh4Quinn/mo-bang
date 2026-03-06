"""热点查询相关接口。"""
from __future__ import annotations

import json
import re
from typing import Any

import httpx
from fastapi import APIRouter

router = APIRouter()

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)
DOUYIN_URL = "https://www.iesdouyin.com/web/api/v2/hotsearch/billboard/word/"
XHS_EXPLORE_URL = "https://www.xiaohongshu.com/explore"


async def _fetch_douyin_trends() -> list[dict[str, Any]]:
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(DOUYIN_URL, headers={"User-Agent": USER_AGENT})
        resp.raise_for_status()
        payload = resp.json()

    results: list[dict[str, Any]] = []
    for item in payload.get("word_list", [])[:10]:
        title = item.get("word")
        if not title:
            continue
        results.append(
            {
                "rank": len(results) + 1,
                "title": title,
                "hot": item.get("hot_value") or 0,
            }
        )
    return results


def _clean_xhs_state(raw_state: str) -> str:
    return raw_state.replace(":undefined", ":null").replace("undefined", "null")


async def _fetch_xiaohongshu_trends() -> list[dict[str, Any]]:
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(
            XHS_EXPLORE_URL,
            headers={"User-Agent": USER_AGENT, "Accept": "text/html"},
        )
        resp.raise_for_status()
        html = resp.text

    match = re.search(r"__INITIAL_STATE__=(\{.*?\})\s*</script>", html, re.S)
    if not match:
        raise ValueError("未能解析小红书页面数据")

    state = json.loads(_clean_xhs_state(match.group(1)))
    feeds = state.get("feed", {}).get("feeds", [])

    results: list[dict[str, Any]] = []
    for item in feeds:
        note = item.get("noteCard", {})
        title = note.get("displayTitle") or note.get("title")
        if not title:
            continue
        liked = note.get("interactInfo", {}).get("likedCount")
        try:
            liked_value = int(liked) if liked is not None else None
        except (TypeError, ValueError):
            liked_value = None
        results.append(
            {
                "rank": len(results) + 1,
                "title": title,
                "likes": liked_value,
            }
        )
        if len(results) >= 10:
            break
    return results


@router.get("/douyin")
async def get_douyin_trends():
    """获取抖音热搜真实数据。"""
    try:
        data = await _fetch_douyin_trends()
        return {"success": True, "source": "douyin-web", "data": data}
    except Exception:
        return {
            "success": False,
            "source": "douyin-web",
            "data": [],
            "message": "抖音热搜获取失败，请稍后重试",
        }


@router.get("/xiaohongshu")
async def get_xiaohongshu_trends():
    """获取小红书热门（探索页）真实数据。"""
    try:
        data = await _fetch_xiaohongshu_trends()
        return {"success": True, "source": "xiaohongshu-explore", "data": data}
    except Exception:
        return {
            "success": False,
            "source": "xiaohongshu-explore",
            "data": [],
            "message": "小红书热门获取失败，请稍后重试",
        }
