from nonebot.log import logger
from pathlib import Path
from typing import Union, Optional
import httpx
import aiofiles


class ResourceError(Exception):
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


async def download_resource(resource_dir: Path, name: str, _type: Optional[str] = None) -> bool:
    '''
        Try to download resources, including fonts, fortune copywriting, but not images.
        For fonts & copywriting, download and save into files when missing. Otherwise, raise ResourceError
    '''
    base_url: str = "https://raw.fastgit.org/MinatoAquaCrews/nonebot_plugin_fortune/master/nonebot_plugin_fortune/resource"

    if isinstance(_type, str):
        url: str = base_url + "/" + _type + "/" + name
    else:
        url: str = base_url + "/" + f"{name}"

    resp = await download_url(url)
    if resp:
        await save_resource(resource_dir, resp)
        if name == "copywriting.json":
            version = resp.json().get("version")
            logger.info(f"Got the latest copywriting.json from repo, version: {version}")

        return True

    return False


async def save_resource(resource_dir: Path, response: httpx.Response) -> None:
    async with aiofiles.open(resource_dir, "wb") as f:
        await f.write(response.content)
