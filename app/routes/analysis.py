"""对标分析相关接口。"""
from statistics import mean
from typing import Any, Dict, List

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class AnalyzeRequest(BaseModel):
    """对标分析请求体。"""

    platform: str
    username: str


def build_demo_posts(username: str, platform: str) -> List[Dict[str, Any]]:
    username = (username or 'demo').strip()
    platform = platform or 'xiaohongshu'
    if platform == 'douyin':
        return [
            {'title': f'{username}：门店老板别再盲目跟风做流量了', 'likes': 4200, 'comments': 380, 'shares': 610, 'style': '观点口播', 'hook': '老板以为没客资，是因为内容不够努力'},
            {'title': f'{username}：同城商家做内容，先别急着拍产品', 'likes': 3600, 'comments': 260, 'shares': 420, 'style': '问题拆解', 'hook': '你发的不是内容，是自说自话'},
            {'title': f'{username}：为什么别人随便拍都比你有咨询', 'likes': 5100, 'comments': 440, 'shares': 790, 'style': '反常识表达', 'hook': '大多数账号死在第一句话'},
        ]
    return [
        {'title': f'{username}：代运营老板最容易踩的3个坑', 'likes': 1800, 'comments': 126, 'saves': 920, 'style': '避坑清单', 'hook': '不是你不会做，是你一开始就找错人了'},
        {'title': f'{username}：为什么同样做案例，你发了没人来问', 'likes': 2400, 'comments': 186, 'saves': 1130, 'style': '案例拆解', 'hook': '你以为你在展示专业，其实用户只看见自嗨'},
        {'title': f'{username}：接单内容别一上来就讲流程', 'likes': 2100, 'comments': 154, 'saves': 980, 'style': '接单向图文', 'hook': '客户不是想听你会什么，是想知道你能解决什么'},
    ]


def summarize_posts(posts: List[Dict[str, Any]], platform: str) -> Dict[str, Any]:
    likes = [int(x.get('likes') or 0) for x in posts]
    interaction_key = 'shares' if platform == 'douyin' else 'saves'
    interaction_values = [int(x.get(interaction_key) or 0) for x in posts]
    top_post = max(posts, key=lambda x: int(x.get('likes') or 0)) if posts else {}
    styles = [x.get('style', '未知') for x in posts]
    hooks = [x.get('hook', '') for x in posts if x.get('hook')]
    style_count: Dict[str, int] = {}
    for style in styles:
        style_count[style] = style_count.get(style, 0) + 1
    dominant_style = sorted(style_count.items(), key=lambda x: (-x[1], x[0]))[0][0] if style_count else '未知'
    return {
        'followers': None,
        'avg_likes': round(mean(likes), 1) if likes else 0,
        'avg_interaction': round(mean(interaction_values), 1) if interaction_values else 0,
        'content_style': dominant_style,
        'topics': [x.get('title', '') for x in posts],
        'top_hook': top_post.get('hook', hooks[0] if hooks else ''),
        'top_post_title': top_post.get('title', ''),
        'analysis': {
            'strengths': [
                '标题都在讲明确问题，用户能快速知道这条内容和自己有没有关系。',
                f'高表现内容普遍采用“{dominant_style}”表达，更容易形成停留。',
                '内容大多先讲问题，再给判断或建议，比较符合运营/获客型表达。',
            ],
            'risks': [
                '当前数据是演示分析，不是实时抓取结果。',
                '如果直接照搬选题结构，容易同质化，最好替换成自己的案例和行业场景。',
            ],
            'suggestions': [
                '先学对方的开头钩子和节奏，不要直接抄完整标题。',
                '优先模仿高互动内容的结构，再换成你自己的客户问题。',
                '把“为什么有人问”和“为什么没人问”做成对比，会更容易出反馈。',
            ],
        },
    }


@router.post('/benchmark')
async def analyze_benchmark(req: AnalyzeRequest):
    """返回演示级对标分析结果，并明确标注当前不是实时抓取。"""
    username = (req.username or '').strip()
    platform = (req.platform or 'xiaohongshu').strip()
    posts = build_demo_posts(username or 'demo', platform)
    summary = summarize_posts(posts, platform)
    return {
        'success': True,
        'message': '当前为演示版对标分析：展示分析结构，不代表已完成实时抓取。',
        'data': {
            'username': username,
            'platform': platform,
            'source': 'demo',
            'realtime': False,
            **summary,
            'samples': posts,
        },
    }
