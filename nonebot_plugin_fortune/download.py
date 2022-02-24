import httpx
from nonebot import logger
import requests
from pathlib import Path
try:
    import ujson as json
except ModuleNotFoundError:
    import json

class DownloadError(Exception):
    pass

async def download(url: str) -> bytes:
    async with httpx.AsyncClient() as client:
        for i in range(3):
            try:
                resp = await client.get(url, timeout=10)
                if resp.status_code != 200:
                    continue
                return resp.content
            except Exception as e:
                logger.warning(f'Error downloading {url}, retry {i}/3: {e}')
    raise DownloadError

async def get_resource(file_path: Path, name: str) -> bool:
    url = f"https://cdn.jsdelivr.net/gh/KafCoppelia/nonebot_plugin_fortune@beta.1/nonebot_plugin_fortune/resource/{name}"
    data = await download(url)
    if data:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    return True