import httpx
from nonebot import logger
from pathlib import Path
from aiocache import cached
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

async def get_resource(res_path: Path, file_type: str, name: str) -> bytes:
    file_path: Path = res_path / file_type / name
    url = f"https://cdn.jsdelivr.net/gh/KafCoppelia/nonebot_plugin_fortune@dev/nonebot_plugin_fortune/resource/{file_type}/{name}"
    data = await download(url)
    if data:
        with file_path.open("wb") as f:
            f.write(data)
            
    if not file_path.exists():
        raise DownloadError
    
    return file_path.read_bytes()

@cached(ttl=600)
async def get_font(res_path: Path, name: str) -> bytes:
    return await get_resource(res_path, "font", name)

@cached(ttl=600)
async def get_fortune(res_path: Path, name: str) -> bytes:
    return await get_resource(res_path, "fortune", name)

@cached(ttl=600)
async def get_theme(res_path: Path, theme: str) -> bytes:
    '''
        区分图片主题与格式
    '''
    return await get_resource(res_path, "img", name)