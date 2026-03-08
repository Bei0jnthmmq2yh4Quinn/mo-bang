from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()
DATA_PATH = Path('/opt/content-tools/data/subscriptions.json')


class SubscriptionBody(BaseModel):
    industry: str = ''
    platform: str = 'xiaohongshu'
    frequency: str = 'daily'
    channel: str = 'telegram'
    target: str = ''
    goal: str = '涨粉'


class PreviewBody(BaseModel):
    industry: str = '通用'
    platform: str = 'xiaohongshu'
    frequency: str = 'daily'
    channel: str = 'telegram'
    target: str = ''
    goal: str = '涨粉'


def load_data() -> Dict[str, List[Dict[str, str]]]:
    if not DATA_PATH.exists():
        return {'items': []}
    try:
        return json.loads(DATA_PATH.read_text())
    except Exception:
        return {'items': []}


def save_data(data: Dict[str, List[Dict[str, str]]]) -> None:
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2))


def build_preview(record: Dict[str, str]) -> Dict[str, str]:
    industry = record.get('industry') or '通用'
    platform = record.get('platform') or 'xiaohongshu'
    goal = record.get('goal') or '涨粉'
    headline = f'【{industry}/{platform}】今天建议优先做一条{goal}向内容'
    summary = f'先从用户最有情绪的热点切入，再落到{industry}场景，最后补一个可执行动作。'
    sample = (
        f'今日建议：{industry}赛道可以围绕一个高讨论热点做{goal}内容。\n'
        f'结构建议：先讲情绪，再讲场景，再讲方法。\n'
        f'适用平台：{platform}。'
    )
    return {'headline': headline, 'summary': summary, 'sample': sample}


@router.get('/drafts')
async def get_drafts():
    data = load_data()
    return {'success': True, 'data': data.get('items', [])}


@router.post('/drafts')
async def save_draft(body: SubscriptionBody):
    data = load_data()
    items = data.get('items', [])
    record = {
        'industry': body.industry.strip() or '通用',
        'platform': body.platform,
        'frequency': body.frequency,
        'channel': body.channel,
        'target': body.target.strip(),
        'goal': body.goal,
    }
    items = [x for x in items if not (x.get('industry') == record['industry'] and x.get('platform') == record['platform'] and x.get('frequency') == record['frequency'] and x.get('goal') == record['goal'])]
    items.insert(0, record)
    data['items'] = items[:20]
    save_data(data)
    return {'success': True, 'message': '订阅草稿已保存到服务端', 'data': record}


@router.post('/preview')
async def preview_push(body: PreviewBody):
    record = {
        'industry': body.industry.strip() or '通用',
        'platform': body.platform,
        'frequency': body.frequency,
        'channel': body.channel,
        'target': body.target.strip(),
        'goal': body.goal,
    }
    preview = build_preview(record)
    return {'success': True, 'message': '已生成推送预览', 'data': {'subscription': record, 'preview': preview}}
