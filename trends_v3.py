from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Tuple

import httpx
from fastapi import APIRouter

router = APIRouter()

USER_AGENT = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
    'AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/120.0.0.0 Safari/537.36'
)
DOUYIN_URL = 'https://www.iesdouyin.com/web/api/v2/hotsearch/billboard/word/'
XHS_EXPLORE_URL = 'https://www.xiaohongshu.com/explore'

INDUSTRY_KEYWORDS: Dict[str, Dict[str, List[str]]] = {
    '餐饮': {
        'core': ['餐饮', '餐饮行业', '餐饮店', '餐饮老板', '门店'],
        'sub': ['火锅', '烧烤', '奶茶', '茶饮', '咖啡', '烘焙', '快餐', '小吃', '酒馆', '中餐', '西餐'],
        'biz': ['客流', '到店', '团购', '外卖', '翻台', '复购', '门头', '定价', '套餐', '活动', '引流'],
        'user': ['顾客', '消费者', '排队', '下单', '探店', '差评', '回头客'],
        'risk': ['倒闭', '涨价', '闭店', '亏损', '成本', '房租', '人工', '食材'],
    },
    '通用': {
        'core': [],
        'sub': [],
        'biz': [],
        'user': [],
        'risk': [],
    },
}

GENERIC_BLOCKLIST = [
    '王毅', '外长', '外交', '国际局势', '发布会', '两会', '国务院', '外交部',
    '明星', '恋情', '离婚', '演唱会', '电影票房', '国际新闻'
]


def _normalize_industry(industry: str) -> str:
    industry = (industry or '通用').strip()
    return industry if industry in INDUSTRY_KEYWORDS else industry


def _keyword_pack(industry: str) -> Dict[str, List[str]]:
    if industry in INDUSTRY_KEYWORDS:
        return INDUSTRY_KEYWORDS[industry]
    words = [w for w in re.split(r'[\s,/，、]+', industry) if w]
    return {
        'core': [industry] + words,
        'sub': [],
        'biz': ['获客', '转化', '客户', '咨询', '成交'],
        'user': ['用户', '顾客', '消费者'],
        'risk': ['成本', '涨价', '下降'],
    }


def _all_keywords(pack: Dict[str, List[str]]) -> List[str]:
    seen = []
    for key in ['core', 'sub', 'biz', 'user', 'risk']:
        for item in pack.get(key, []):
            if item and item not in seen:
                seen.append(item)
    return seen


def _score_title(title: str, pack: Dict[str, List[str]]) -> Tuple[int, List[str]]:
    matched: List[str] = []
    score = 0
    for word in pack.get('core', []):
        if word and word in title:
            matched.append(word)
            score += 5
    for word in pack.get('sub', []):
        if word and word in title:
            matched.append(word)
            score += 4
    for word in pack.get('biz', []):
        if word and word in title:
            matched.append(word)
            score += 3
    for word in pack.get('user', []):
        if word and word in title:
            matched.append(word)
            score += 2
    for word in pack.get('risk', []):
        if word and word in title:
            matched.append(word)
            score += 2
    return score, matched


def _is_blocked_generic(title: str) -> bool:
    return any(word in title for word in GENERIC_BLOCKLIST)


def _filter_industry_items(industry: str, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    industry = _normalize_industry(industry)
    if industry == '通用':
        return items[:5]

    pack = _keyword_pack(industry)
    ranked: List[Dict[str, Any]] = []
    for item in items:
        title = str(item.get('title') or '').strip()
        if not title:
            continue
        if _is_blocked_generic(title):
            continue
        score, matched = _score_title(title, pack)
        if score <= 0:
            continue
        row = dict(item)
        row['relevance_score'] = score
        row['matched_keywords'] = matched
        ranked.append(row)

    ranked.sort(key=lambda x: (x.get('relevance_score', 0), x.get('hot', 0), x.get('likes', 0)), reverse=True)
    return ranked[:5]


FALLBACK_TEMPLATES: Dict[str, List[Dict[str, str]]] = {
    '餐饮': [
        {
            'hotspot': '餐饮客流下滑',
            'reason': '虽然没抓到高相关实时热点，但“客流/到店/复购”一直是餐饮老板最关心的经营问题。',
            'topic': '餐饮店最近没客流，不一定是你产品差，可能是内容没把进店理由说清楚',
            'angle': '门店经营问题拆解',
            'action': '先讲客流问题，再讲进店理由，最后补一个能马上改的动作。',
            'matched_keywords': ['餐饮', '客流', '门店'],
            'relevance_score': 10,
        },
        {
            'hotspot': '餐饮团购转化',
            'reason': '团购和到店转化是餐饮行业稳定高相关话题，比泛热点更适合直接拿来做内容。',
            'topic': '餐饮团购没人下单，很多时候不是便宜不够，而是套餐看起来没有购买理由',
            'angle': '转化问题切入',
            'action': '拆价格、拆套餐、拆下单理由，最后给一个重做套餐文案的动作。',
            'matched_keywords': ['餐饮', '团购', '转化'],
            'relevance_score': 9,
        },
        {
            'hotspot': '餐饮外卖复购',
            'reason': '外卖和复购属于餐饮高频经营场景，适合长期做系列内容。',
            'topic': '餐饮外卖单量一般，不是平台不给流量，是顾客吃完一次没有理由再点第二次',
            'angle': '复购经营视角',
            'action': '先说复购，再说顾客感知，最后给一个可执行优化点。',
            'matched_keywords': ['餐饮', '外卖', '复购'],
            'relevance_score': 9,
        },
    ]
}


def build_industry_suggestions(industry: str, platform: str, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    industry = _normalize_industry(industry)
    platform = platform or 'xiaohongshu'
    filtered = _filter_industry_items(industry, items)
    if not filtered:
        return FALLBACK_TEMPLATES.get(industry, [
            {
                'hotspot': f'{industry}经营问题',
                'reason': f'暂时没抓到高相关实时热点，先回到 {industry} 行业稳定存在的经营问题。',
                'topic': f'{industry}内容别追泛热点，先讲用户真正在意的问题',
                'angle': '行业问题切入',
                'action': '先讲痛点，再讲原因，最后给一个马上能做的动作。',
                'matched_keywords': [industry],
                'relevance_score': 6,
            }
        ])

    suggestions = []
    for item in filtered:
        title = item.get('title') or '未命名热点'
        matched = item.get('matched_keywords') or []
        suggestions.append(
            {
                'hotspot': title,
                'reason': f'标题命中了 {"、".join(matched)}，和 {industry} 行业直接相关，不是泛热点硬套。',
                'topic': f'{industry}怎么结合「{title}」做一条更容易出反馈的内容',
                'angle': '小红书图文拆解' if platform == 'xiaohongshu' else '抖音口播借势',
                'action': '先讲行业情绪，再补经营场景，最后落到具体建议。',
                'matched_keywords': matched,
                'relevance_score': item.get('relevance_score', 0),
            }
        )
    return suggestions


def build_today_brief(industry: str, platform: str, goal: str, items: List[Dict[str, Any]]) -> Dict[str, Any]:
    suggestions = build_industry_suggestions(industry, platform, items)
    first = suggestions[0] if suggestions else {
        'topic': f'{industry}今天适合做一条{goal}向内容',
        'reason': '当前没有抓到合适热点，建议先用行业问题切入。',
        'action': '先讲痛点，再讲方法，最后加行动引导。',
        'hotspot': '通用话题',
        'angle': '通用切入',
        'matched_keywords': [],
        'relevance_score': 0,
    }
    return {
        'industry': industry,
        'platform': platform,
        'goal': goal,
        'headline': first['topic'],
        'reason': first['reason'],
        'action': first['action'],
        'hotspot': first['hotspot'],
        'angle': first['angle'],
        'matched_keywords': first.get('matched_keywords', []),
        'relevance_score': first.get('relevance_score', 0),
        'title_hint': f'{industry}{goal}内容，可以先从「{first["hotspot"]}」切入',
    }


async def _fetch_douyin_trends() -> List[Dict[str, Any]]:
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(DOUYIN_URL, headers={'User-Agent': USER_AGENT})
        resp.raise_for_status()
        payload = resp.json()
    results = []
    for item in payload.get('word_list', [])[:20]:
        title = item.get('word')
        if not title:
            continue
        results.append({'rank': len(results) + 1, 'title': title, 'hot': item.get('hot_value') or 0})
    return results


def _clean_xhs_state(raw_state: str) -> str:
    return raw_state.replace(':undefined', ':null').replace('undefined', 'null')


async def _fetch_xiaohongshu_trends() -> List[Dict[str, Any]]:
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(XHS_EXPLORE_URL, headers={'User-Agent': USER_AGENT, 'Accept': 'text/html'})
        resp.raise_for_status()
        html = resp.text
    match = re.search(r'__INITIAL_STATE__=(\{.*?\})\s*</script>', html, re.S)
    if not match:
        raise ValueError('未能解析小红书页面数据')
    state = json.loads(_clean_xhs_state(match.group(1)))
    feeds = state.get('feed', {}).get('feeds', [])
    results = []
    for item in feeds:
        note = item.get('noteCard', {})
        title = note.get('displayTitle') or note.get('title')
        if not title:
            continue
        liked = note.get('interactInfo', {}).get('likedCount')
        try:
            liked_value = int(liked) if liked is not None else None
        except (TypeError, ValueError):
            liked_value = None
        results.append({'rank': len(results) + 1, 'title': title, 'likes': liked_value or 0})
        if len(results) >= 20:
            break
    return results


@router.get('/douyin')
async def get_douyin_trends():
    try:
        data = await _fetch_douyin_trends()
        return {'success': True, 'source': 'douyin-web', 'data': data}
    except Exception:
        return {'success': False, 'source': 'douyin-web', 'data': [], 'message': '抖音热搜获取失败，请稍后重试'}


@router.get('/xiaohongshu')
async def get_xiaohongshu_trends():
    try:
        data = await _fetch_xiaohongshu_trends()
        return {'success': True, 'source': 'xiaohongshu-explore', 'data': data}
    except Exception:
        return {'success': False, 'source': 'xiaohongshu-explore', 'data': [], 'message': '小红书热门获取失败，请稍后重试'}


@router.get('/suggestions')
async def get_trend_suggestions(industry: str = '通用', platform: str = 'xiaohongshu'):
    try:
        data = await (_fetch_xiaohongshu_trends() if platform == 'xiaohongshu' else _fetch_douyin_trends())
        suggestions = build_industry_suggestions(industry, platform, data)
        return {'success': True, 'industry': industry, 'platform': platform, 'data': suggestions}
    except Exception:
        suggestions = build_industry_suggestions(industry, platform, [])
        return {'success': True, 'industry': industry, 'platform': platform, 'data': suggestions, 'message': '实时热点获取失败，已返回行业兜底建议'}


@router.get('/brief')
async def get_today_brief(industry: str = '通用', platform: str = 'xiaohongshu', goal: str = '涨粉'):
    try:
        data = await (_fetch_xiaohongshu_trends() if platform == 'xiaohongshu' else _fetch_douyin_trends())
        brief = build_today_brief(industry, platform, goal, data)
        return {'success': True, 'data': brief}
    except Exception:
        brief = build_today_brief(industry, platform, goal, [])
        return {'success': True, 'data': brief, 'message': '实时热点获取失败，已返回行业兜底建议'}
