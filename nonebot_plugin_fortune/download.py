from nonebot import logger
from typing import Union
import httpx

class DownloadError(Exception):
    def __init__(self, msg):
        self.msg = msg
        
    def __str__(self):
        return self.msg

async def download_url(url: str) -> Union[httpx.Response, None]:
    async with httpx.AsyncClient() as client:
        for i in range(3):
            try:
                resp = await client.get(url, timeout=10)
                if resp.status_code != 200:
                    continue
                return resp
            except Exception:
                logger.warning(f"Error downloading {url}, retry: {i}/3")
    
    logger.warning(f"Abort downloading")           
    return None