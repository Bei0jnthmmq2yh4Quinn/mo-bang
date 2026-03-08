"""媒体处理相关接口。"""
from fastapi import APIRouter

router = APIRouter()


@router.get('/download')
async def download_media(url: str):
    """返回当前能力边界，避免误导用户以为已经接入真实下载。"""
    return {
        'success': False,
        'implemented': False,
        'message': '媒体下载功能暂未接入站内下载链路，当前仅支持复制命令手动执行。',
        'example': f"yt-dlp '{url}'",
    }
