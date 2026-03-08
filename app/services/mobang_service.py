from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple

import httpx

DEFAULT_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
DEFAULT_BASE_URL = os.getenv('OPENAI_BASE_URL', 'https://api.003636.xyz/v1')
DEFAULT_API_KEY = os.getenv('OPENAI_API_KEY', '')


class MobangService:
    @staticmethod
    def split_sentences(text: str) -> List[str]:
        parts = re.split(r'[。！？!?.\n]+', text)
        return [p.strip() for p in parts if p.strip()]

    @classmethod
    def build_context(cls, industry: str = '', platform: str = '', goal: str = '') -> Dict[str, str]:
        industry = (industry or '通用').strip()
        platform = (platform or 'xiaohongshu').strip()
        goal = (goal or '涨粉').strip()
        return {'industry': industry, 'platform': platform, 'goal': goal}

    @classmethod
    def rule_analyze(cls, text: str, industry: str = '', platform: str = '', goal: str = '') -> Dict[str, Any]:
        ctx = cls.build_context(industry, platform, goal)
        sentences = cls.split_sentences(text)
        hook = sentences[0] if sentences else text[:30]
        topic = ' / '.join(sentences[:2])[:60] if sentences else '未识别'
        emotion = '情绪刺激强，适合做开头钩子' if any(k in text for k in ['一定', '千万', '真的', '立刻', '马上', '为什么']) else '偏理性表达，可加强冲突感'
        cta = '结尾补一句“你更适合哪种做法？评论区聊聊”。' if ctx['goal'] == '涨粉' else ('结尾补一句“如果你也想做这类内容，可以直接来聊”。' if ctx['goal'] in ['转化', '接单'] else '结尾补一句“你最想先改哪一步？”')
        structure = []
        if sentences:
            structure.append(f'1. 开头钩子：{sentences[0]}')
        if len(sentences) > 1:
            structure.append(f'2. 问题展开：{sentences[1]}')
        if len(sentences) > 2:
            structure.append(f'3. 解决方案/案例：{"；".join(sentences[2:4])}')
        if len(sentences) > 4:
            structure.append(f'4. 收尾总结：{sentences[-1]}')
        platform_tip = '适合拆成小红书图文结构' if ctx['platform'] == 'xiaohongshu' else '适合压缩成短视频口播节奏'
        goal_tip = {
            '涨粉': '重点强化情绪钩子和共鸣停留。',
            '转化': '重点强化结果承诺、信任细节和行动引导。',
            '接单': '重点展示专业判断、案例和服务感。',
            '案例展示': '重点突出前后变化和方法论。',
        }.get(ctx['goal'], '根据目标调整表达重点。')
        return {
            'hook': hook,
            'topic': topic,
            'emotion': emotion,
            'cta': cta,
            'structure': structure,
            'why_it_works': f'这类内容容易传播，因为它有明确钩子、具体场景、低理解门槛。对于{ctx["industry"]}赛道，{platform_tip}',
            'risks': '如果直接照搬原句和原案例，容易变成低质量模仿。建议保留结构，替换场景、对象和表达习惯。',
            'suggestions': [
                f'把第一句换成更贴近{ctx["industry"]}用户的痛点表达。',
                '加入一个你自己真实经历或客户案例。',
                goal_tip,
            ],
            'angles': [
                f'{ctx["industry"]}行业反常识切入',
                f'{ctx["industry"]}用户痛点共鸣切入',
                f'{ctx["industry"]}案例对比切入',
            ],
            'context': ctx,
            'fallback': True,
        }

    @classmethod
    def _build_variant(cls, mode: str, tone: str, hook: str, ctx: Dict[str, str]) -> Dict[str, str]:
        industry = ctx['industry']
        goal = ctx['goal']
        if mode == 'douyin':
            if tone == 'strong':
                script = f"{hook}。\n\n很多{industry}内容发不起来，不是你不努力，是你一开口就没抓住人。\n\n先把最扎心的问题甩出来，再给一个立刻能用的方法，再补一句：如果你也踩过这个坑，评论区打个1。"
                title = '抖音强情绪版'
                summary = f'更强冲击感，更适合{industry}短视频口播开场。'
            elif tone == 'convert':
                script = f"{hook}。\n\n如果你做{industry}内容是想拿{goal}结果，别一上来就讲过程。\n\n先说用户最关心的结果，再给方法，再告诉他你能怎么帮。\n\n最后一句直接收口：想按你的行业改，我可以继续帮你顺。"
                title = '抖音转化版'
                summary = '更强调结果、信任和转化。'
            else:
                script = f"{hook}。\n\n很多人做{industry}内容没结果，不是因为不努力，而是第一句就没人想听。\n\n你要先把问题说到用户心里，再给一个马上能用的做法，最后再补一句让人愿意互动的话。\n\n整条控制在 30 到 60 秒，句子短一点，口语感重一点。"
                title = '抖音稳妥版'
                summary = '节奏稳定，适合 30~60 秒口播。'
        elif mode == 'xiaohongshu':
            if tone == 'strong':
                script = f"标题建议：{hook}\n\n很多做{industry}的人以为内容没反馈，是因为选题不行。\n其实更常见的问题是：第一段就没人想继续看。\n\n更好的写法：先把痛点戳破，再给方法，最后给一个马上能照做的小动作。\n\n这种结构更适合做成 3-5 段短图文。"
                title = '小红书强钩子版'
                summary = '更强调停留和点击。'
            elif tone == 'convert':
                script = f"标题建议：{hook}\n\n如果你的{industry}内容还承担{goal}，那表达顺序比你想的更重要。\n\n先说结果，再说过程，再补一个真实案例，用户更容易信你。\n\n结尾记得留一个轻转化口，比如：有同类问题的可以直接聊。"
                title = '小红书转化版'
                summary = '更适合接单、案例、服务型内容。'
            else:
                script = f"标题建议：{hook}\n\n今天想聊一个很多做{industry}内容的人都会踩的点。\n\n为什么同样的内容，别人发了有反馈，你发了却没动静？问题往往不在内容本身，而在表达顺序。\n\n更好的写法是：先抛痛点，再给方法，最后给一个能马上照做的小动作。\n\n整体更适合图文分段表达，每段别太长。"
                title = '小红书稳妥版'
                summary = '更适合图文或口播转图文。'
        elif mode == 'lead':
            if tone == 'strong':
                script = f"{hook}。\n\n很多{industry}老板不是不愿意做内容，是做了半天发现根本没人来问。\n\n问题不一定是内容量不够，而是你发的内容没有对准客户真正关心的结果。\n\n如果你现在也卡在这一步，先别急着继续堆内容。"
                title = '接单强筛选版'
                summary = '更适合直接筛选潜在客户。'
            elif tone == 'convert':
                script = f"{hook}。\n\n如果你做{industry}内容的目标是{goal}，那你的内容里一定要先让客户看到结果，再看到方法。\n\n当用户觉得你真的懂他的问题，转化才会发生。\n\n如果你想按行业拆一版适合你的内容结构，可以继续往下聊。"
                title = '接单转化版'
                summary = '更适合私信、咨询、接单场景。'
            else:
                script = f"{hook}。\n\n很多老板发内容没反馈，不代表平台不行，更可能是内容表达顺序不对。\n\n先把客户最在意的问题说出来，再给方法，再讲你能提供什么帮助。\n\n这样写，内容才更容易带来咨询。"
                title = '接单稳妥版'
                summary = '偏咨询导向，更适合服务型账号。'
        elif mode == 'spoken':
            title = '口播顺稿版'
            summary = '句子更短，停顿更明显，适合直接念。'
            script = f"{hook}。\n\n先说结论。\n很多{industry}内容没反馈，不是你没发，而是你一开口就太平。\n\n你要先说问题。\n再说为什么会这样。\n再给一个能马上照做的方法。\n\n最后补一句互动或者行动引导。"
        elif mode == 'opinion':
            title = '观点表达版'
            summary = '更强调判断、立场和反常识表达。'
            script = f"{hook}。\n\n我越来越觉得，很多{industry}内容做不起来，不是不会写，而是不敢下判断。\n\n你越想把所有人都讲明白，内容越容易没有记忆点。\n\n真正有反馈的表达，往往都有明确立场。"
        else:
            title = f'{mode}改写版'
            summary = f'根据{industry}场景做出的改写。'
            script = f"先说结论：{hook}。\n再把问题、方法和行动建议讲清楚。"
        return {'tone': tone, 'title': title, 'summary': summary, 'script': script}

    @classmethod
    def _build_xhs_package(cls, hook: str, ctx: Dict[str, str], variants: List[Dict[str, str]]) -> Dict[str, Any]:
        industry = ctx['industry']
        goal = ctx['goal']
        title_main = f'{industry}内容怎么写，反馈才会更好'
        titles = [
            title_main,
            f'{industry}做{goal}内容，别再一上来就讲自己',
            f'为什么你发了{industry}内容，还是没人来问',
        ]
        copywriting = (
            f'{hook}。\n\n'
            f'很多做{industry}内容的人没结果，不是因为不努力，而是内容一开口就偏了。\n\n'
            f'用户真正想看的，不是你会什么，而是你到底能帮他解决什么问题。\n\n'
            f'更稳的写法是：先把用户最在意的痛点讲透，再给一个可执行的方法，最后补一句明确的行动引导。\n\n'
            f'比如你做{industry}内容，如果目标是{goal}，那正文顺序最好是：先戳问题，再给判断，再给一个能立刻照做的小动作。\n\n'
            f'你可以先别急着证明自己多专业，先让用户觉得“这条就是在说我”。\n\n'
            f'结尾再补一句行动引导，比如：如果你也在做这类内容，但一直没有反馈，可以把你的行业和目标发我，我按你的方向继续帮你顺。'
        )
        tags = [industry, goal, '内容运营', '小红书文案', '爆款拆解', '内容改写', '获客内容']
        return {
            'titles': titles,
            'copywriting': copywriting,
            'tags': tags,
            'primary_title': titles[0],
            'outline': [
                '开头：先戳用户当前最容易踩的坑',
                '中段：解释为什么没反馈，不是努力不够，而是表达顺序不对',
                '后段：给一个能直接套用的写法或动作',
                '结尾：加行动引导，推动评论或私信',
            ],
            'primary_variant': variants[0] if variants else None,
        }

    @classmethod
    def rule_rewrite(cls, text: str, mode: str, industry: str = '', platform: str = '', goal: str = '') -> Dict[str, Any]:
        ctx = cls.build_context(industry, platform, goal)
        base = cls.rule_analyze(text, industry=industry, platform=platform, goal=goal)
        hook = base['hook']
        variants = [
            cls._build_variant(mode, 'safe', hook, ctx),
            cls._build_variant(mode, 'strong', hook, ctx),
            cls._build_variant(mode, 'convert', hook, ctx),
        ]
        xhs_package = cls._build_xhs_package(hook, ctx, variants) if ctx['platform'] == 'xiaohongshu' or mode == 'xiaohongshu' else None
        return {
            'mode': mode,
            'title': variants[0]['title'],
            'summary': f'已生成 3 个方向，分别偏稳妥、强钩子、转化，当前按{ctx["industry"]}/{ctx["platform"]}/{ctx["goal"]}场景调整。',
            'script': variants[0]['script'],
            'variants': variants,
            'xhs_package': xhs_package,
            'context': ctx,
            'fallback': True,
        }

    @classmethod
    async def _chat_json(cls, prompt: str, *, api_key: str, base_url: str, model: str) -> Dict[str, Any]:
        payload = {
            'model': model,
            'messages': [
                {'role': 'system', 'content': '你是结构化 JSON 输出助手，只输出合法 JSON。'},
                {'role': 'user', 'content': prompt},
            ],
            'temperature': 0.7,
        }
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(f'{base_url.rstrip("/")}/chat/completions', headers={'Authorization': f'Bearer {api_key}'}, json=payload)
            r.raise_for_status()
            data = r.json()
        content = data['choices'][0]['message']['content']
        return json.loads(content)

    @classmethod
    async def llm_analyze(cls, text: str, *, api_key: str, base_url: str, model: str, industry: str = '', platform: str = '', goal: str = '') -> Optional[Dict[str, Any]]:
        if not api_key:
            return None
        prompt = (
            '你是内容拆解助手。请结合以下上下文进行拆解：'
            f'行业={industry or "通用"}，平台={platform or "xiaohongshu"}，目标={goal or "涨粉"}。'
            '输出 JSON，字段必须包含：hook, topic, emotion, cta, structure(数组), why_it_works, risks, suggestions(数组), angles(数组), context(对象)。只返回 JSON。\n\n文本：' + text
        )
        obj = await cls._chat_json(prompt, api_key=api_key, base_url=base_url, model=model)
        obj['fallback'] = False
        return obj

    @classmethod
    async def llm_rewrite(cls, text: str, mode: str, *, api_key: str, base_url: str, model: str, industry: str = '', platform: str = '', goal: str = '') -> Optional[Dict[str, Any]]:
        if not api_key:
            return None
        prompt = (
            '你是内容改写助手，同时要具备小红书成稿能力。请结合以下上下文改写：'
            f'行业={industry or "通用"}，平台={platform or "xiaohongshu"}，目标={goal or "涨粉"}，模式={mode}。'
            '返回 JSON，字段必须包含：mode, title, summary, script, variants(数组，至少3项，每项包含 tone,title,summary,script), context(对象)。'
            '当平台是 xiaohongshu 或模式是 xiaohongshu 时，额外返回 xhs_package 对象，字段包含 titles(3个标题数组), copywriting(完整正文), tags(5-8个标签数组), primary_title。只返回 JSON。\n\n原文：' + text
        )
        obj = await cls._chat_json(prompt, api_key=api_key, base_url=base_url, model=model)
        obj['fallback'] = False
        return obj

    @classmethod
    def resolve_provider(cls, provider: Optional[Dict[str, Any]]) -> Tuple[str, str, str]:
        provider = provider or {}
        api_key = (provider.get('api_key') or '').strip() or DEFAULT_API_KEY
        base_url = (provider.get('base_url') or '').strip() or DEFAULT_BASE_URL
        model = (provider.get('model') or '').strip() or DEFAULT_MODEL
        return api_key, base_url, model
