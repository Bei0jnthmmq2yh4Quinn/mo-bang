from __future__ import annotations

import re
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class AnalyzeBody(BaseModel):
    text: str = ""
    url: str = ""


class RewriteBody(BaseModel):
    text: str = ""
    url: str = ""
    mode: str = "douyin"


def _normalize_text(text: str, url: str) -> tuple[Optional[str], Optional[str]]:
    text = (text or '').strip()
    url = (url or '').strip()
    if text:
        return text, None
    if url:
        if 'douyin.com' in url or 'iesdouyin.com' in url:
            return None, '当前抖音链接解析先留占位，建议先把字幕/文案贴进来再拆解。'
        return None, '暂不支持该链接类型，请先粘贴文本内容。'
    return None, '请先输入爆款文案、字幕或链接。'


def _split_sentences(text: str) -> list[str]:
    parts = re.split(r'[。！？!?.\n]+', text)
    return [p.strip() for p in parts if p.strip()]


def _analyze_text(text: str) -> dict:
    sentences = _split_sentences(text)
    hook = sentences[0] if sentences else text[:30]
    topic = ' / '.join(sentences[:2])[:60] if sentences else '未识别'
    emotion = '情绪刺激强，适合做开头钩子' if any(k in text for k in ['一定', '千万', '真的', '立刻', '马上', '为什么']) else '偏理性表达，可加强冲突感'
    cta = '结尾补一句“你更适合哪种做法？评论区聊聊”。'
    structure = []
    if sentences:
        structure.append(f'1. 开头钩子：{sentences[0]}')
    if len(sentences) > 1:
        structure.append(f'2. 问题展开：{sentences[1]}')
    if len(sentences) > 2:
        structure.append(f'3. 解决方案/案例：{"；".join(sentences[2:4])}')
    if len(sentences) > 4:
        structure.append(f'4. 收尾总结：{sentences[-1]}')
    why = '这类内容容易传播，因为它有明确钩子、具体场景、低理解门槛，并且能让用户迅速代入自己的处境。'
    return {
        'hook': hook,
        'topic': topic,
        'emotion': emotion,
        'cta': cta,
        'structure': structure,
        'why_it_works': why,
    }


def _rewrite_text(text: str, mode: str) -> dict:
    base = _analyze_text(text)
    title_map = {
        'douyin': '抖音口播改写版',
        'xiaohongshu': '小红书图文改写版',
        'spoken': '更口语的表达版',
        'lead': '更适合接单转化版',
        'opinion': '更适合观点输出版',
    }
    intro_map = {
        'douyin': '开头直接抛观点，节奏更快，适合 30~60 秒口播。',
        'xiaohongshu': '加强标题感与结构感，更适合图文或口播转图文。',
        'spoken': '整体更像真人说话，减少书面感。',
        'lead': '强化结果、信任和案例表达，更适合转化与接单。',
        'opinion': '加强态度和判断，更适合做观点型内容。',
    }

    hook = base['hook']
    if mode == 'douyin':
        script = f"{hook}。\n\n很多人做内容没结果，不是因为不努力，而是第一句就没人想听。\n\n你要先把问题说到用户心里，再给一个马上能用的做法，最后再补一句让人愿意互动的话。\n\n所以这类内容最关键的不是信息量，而是节奏、冲突和代入感。\n\n如果你也在做同类内容，先把开头那一句改了，数据通常就会不一样。"
    elif mode == 'xiaohongshu':
        script = f"标题建议：{hook}\n\n今天想聊一个很多人都会踩的点。\n\n为什么同样的内容，别人发了有反馈，你发了却没动静？问题往往不在内容本身，而在表达顺序。\n\n更好的写法是：先抛痛点，再给方法，最后给一个能马上照做的小动作。\n\n如果你最近也在卡这个问题，可以先从第一屏开始改。"
    elif mode == 'spoken':
        script = f"其实很多人都忽略了一个点：{hook}。\n\n你以为内容没效果，是内容不行；但很多时候，问题只是你讲得不够直接。\n\n你先把用户最痛的那个点说出来，再往下讲方法，别人就更容易听进去。\n\n所以别一上来铺垫太多，直接进主题，效果会好很多。"
    elif mode == 'lead':
        script = f"{hook}。\n\n我发现很多账号内容做了不少，但就是接不到单，核心问题不是不会做，而是不会把价值讲清楚。\n\n真正能带来转化的内容，通常都有三个点：先说结果，再说过程，再说你能怎么帮到别人。\n\n如果你也想把内容做成信任资产，这个结构可以直接拿去用。"
    else:
        script = f"先说结论：{hook}。\n\n大部分人把注意力放在细枝末节上，却忽略了真正决定传播效果的是内容的切入角度。\n\n一条内容之所以能爆，不只是因为信息对，而是它把用户的情绪、立场和场景一下子拉进来了。\n\n所以做内容时，别只问写了什么，更要问：这个角度有没有判断，有没有态度。"

    return {
        'mode': mode,
        'title': title_map.get(mode, '改写版'),
        'summary': intro_map.get(mode, '根据原内容做出的改写。'),
        'script': script,
    }


@router.post('/analyze')
async def analyze(body: AnalyzeBody):
    text, err = _normalize_text(body.text, body.url)
    if err:
        return {'success': False, 'message': err, 'data': None}
    return {'success': True, 'message': '拆解完成', 'data': _analyze_text(text)}


@router.post('/rewrite')
async def rewrite(body: RewriteBody):
    text, err = _normalize_text(body.text, body.url)
    if err:
        return {'success': False, 'message': err, 'data': None}
    return {'success': True, 'message': '改写完成', 'data': _rewrite_text(text, body.mode)}
