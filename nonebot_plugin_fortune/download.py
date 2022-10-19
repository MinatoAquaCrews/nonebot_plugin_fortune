from nonebot.log import logger
from pathlib import Path
from typing import Union, Optional
import httpx
import aiofiles
from aiocache import cached

class DownloadError(Exception):
    def __init__(self, msg):
        self.msg = msg
        
    def __str__(self):
        return self.msg

async def download_url(url: str) -> Union[httpx.Response, None]:
    async with httpx.AsyncClient() as client:
        for i in range(3):
            try:
                resp = await client.get(url, timeout=20)
                if resp.status_code != 200:
                    continue
                return resp
            except Exception:
                logger.warning(f"Error occurred when downloading {url}, retry: {i+1}/3")
    
    logger.warning(f"Abort downloading")
    return None

async def download_resource(name: str, _type: Optional[str] = None, theme: Optional[str] = None) -> Union[httpx.Response, None]:
    '''
        Try to download resources, including fonts, fortune copywriting, images.
        For fonts & copywriting, download and save into files when missing.
        For images, cache or saving. Optional for user's setting
    '''
    base_url: str = "https://raw.fastgit.org/MinatoAquaCrews/nonebot_plugin_fortune/beta/nonebot_plugin_fortune/resource"
    
    if isinstance(_type, str):
        if isinstance(theme, str):
            url: str = base_url + "/" + f"{_type}" + "/" + f"{theme}" + "/" + f"{name}"
        else:
            url: str = base_url + "/" + f"{_type}" + "/" + f"{name}"
    else:
        url: str = base_url + "/" + f"{name}"
    
    return await download_url(url)

@cached(ttl=120)
async def download_images(theme: str, name: str) -> Union[httpx.Response, None]:
    url: str = "https://raw.fastgit.org/MinatoAquaCrews/nonebot_plugin_fortune/beta/nonebot_plugin_fortune/resource/img/" + f"{theme}/{name}"
    return await download_url(url)

async def save_resource(resource_dir: Path, name: str, response: httpx.Response) -> None:
    async with aiofiles.open(resource_dir / name, "wb") as f:
        await f.write(response.content)