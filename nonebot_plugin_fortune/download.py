import json
from pathlib import Path
from typing import Any, Dict, Optional

import httpx
from nonebot.log import logger


class ResourceError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg

    __repr__ = __str__


async def download_url(url: str) -> Optional[Dict[str, Any]]:
    async with httpx.AsyncClient() as client:
        for i in range(3):
            try:
                resp = await client.get(url, timeout=20)
                if resp.status_code != 200:
                    continue

                return resp.json()

            except Exception:
                logger.warning(f"Error occurred when downloading {url}, retry: {i+1}/3")

    logger.warning("Abort downloading")
    return None


async def download_resource(
    resource_dir: Path, name: str, _type: Optional[str] = None
) -> bool:
    """
    Try to download resources, json but not images.
    For fonts & copywriting, download and save into files when missing. Otherwise, raise ResourceError.
    """
    base_url: str = "https://raw.fgit.ml/MinatoAquaCrews/nonebot_plugin_fortune/master/nonebot_plugin_fortune/resource"

    if isinstance(_type, str):
        url: str = base_url + "/" + _type + "/" + name
    else:
        url: str = base_url + "/" + f"{name}"

    resp = await download_url(url)
    if resp:
        save_json(resource_dir, resp)
        if name == "copywriting.json":
            version: float = resp.get("version", 0)
            logger.info(
                f"Got the latest copywriting.json from repo, version: {version}"
            )

        return True

    return False


def save_json(_file: Path, _data: Dict[str, Any]) -> None:
    with open(_file, "w", encoding="utf-8") as f:
        json.dump(_data, f, ensure_ascii=False, indent=4)
