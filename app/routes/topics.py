"""AI 选题相关接口。"""
from __future__ import annotations

from pydantic import BaseModel
from fastapi import APIRouter

router = APIRouter()


class TopicRequest(BaseModel):
    """选题生成请求体。"""

    niche: str
    benchmark_topics: list[str] = []
    trends: list[str] = []


@router.post("/generate")
async def generate_topics(req: TopicRequest):
    """基于领域、对标选题和热点生成结构化选题。"""
    niche = req.niche or "通用"
    trend = req.trends[0] if req.trends else "本周热点"
    benchmark = req.benchmark_topics[0] if req.benchmark_topics else "高赞模板"

    topics = [
        {
            "title": f"{niche}如何结合「{trend}」快速起量",
            "type": "热点融合",
            "angle": "趋势解读",
            "format": "清单/图文",
            "hook": "开头用对比数据制造紧迫感",
            "points": [
                f"{trend}背后的用户情绪",
                f"{niche}可直接套用的3个切入点",
                "结尾给可复制模板",
            ],
            "hashtags": [f"#{niche}", f"#{trend}", "#内容运营"],
        },
        {
            "title": f"{benchmark}拆解：{niche}爆款结构复用",
            "type": "对标拆解",
            "angle": "结构复用",
            "format": "长图文/步骤",
            "hook": "第一屏直接给结论+截图",
            "points": [
                "标题公式与封面关键词",
                "内容节奏（开场-干货-复盘）",
                "评论区引导话术",
            ],
            "hashtags": [f"#{niche}", "#对标分析", "#爆款拆解"],
        },
        {
            "title": f"{niche}新手避坑：90%人忽略的细节",
            "type": "知识干货",
            "angle": "避坑清单",
            "format": "短图文/条列",
            "hook": "前3条直接反常识",
            "points": [
                "常见误区 + 反例",
                "正确做法 + 最小行动",
                "可复用检查表",
            ],
            "hashtags": [f"#{niche}", "#新手避坑", "#干货"],
        },
    ]

    return {"success": True, "data": topics}
