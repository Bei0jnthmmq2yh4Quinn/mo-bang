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
    }
    items = [x for x in items if not (x.get('industry') == record['industry'] and x.get('platform') == record['platform'] and x.get('frequency') == record['frequency'])]
    items.insert(0, record)
    data['items'] = items[:20]
    save_data(data)
    return {'success': True, 'message': '订阅草稿已保存到服务端', 'data': record}
