from nonebot import logger
from pathlib import Path
from typing import Union
from aiocache import cached
import aiofiles
import httpx

class DownloadError(Exception):
    def __init__(self, msg):
        self.msg = msg
        
    def __str__(self):
        return self.msg

async def download(url: str) -> Union[bytes, None]:
    async with httpx.AsyncClient() as client:
        for i in range(3):
            try:
                resp = await client.get(url, timeout=10)
                if resp.status_code != 200:
                    continue
                return resp.content
            except Exception as e:
                logger.warning(f'Error downloading {url}, retry {i}/3: {e}')
                
    return None

async def get_resource(_path: Path, _type: str, _name: str) -> None:
    '''
        Try to download from repo
        - _path: where to save
        - _type: font, fortune, or img
        - _name: name of resource. Image needs: "_theme/_charac"
        The function of downloading all images from themes is under consideration
    '''
    file_path: Path = _path / _type / _name
    url = f"https://raw.fastgit.org/MinatoAquaCrews/nonebot_plugin_fortune/dev/nonebot_plugin_fortune/resource/{_type}/{_name}"
    
    data = await download(url)
    if data:
        await save_resource(file_path, data)
    else:
        raise DownloadError(f"Resource of Fortune plugin missing: {_type}/{_name}! Please check!")
    
    # return file_path.read_bytes()

async def save_resource(_path: Path, _response: bytes) -> None:
    '''
        Save bytes into file: _path
    '''
    async with aiofiles.open(_path, "wb") as f:
        await f.write(_response)

@cached(ttl=600)
async def get_font(_path: Path, _name: str) -> None:
    return await get_resource(_path, "font", _name)

@cached(ttl=600)
async def get_fortune(_path: Path, _name: str) -> None:
    return await get_resource(_path, "fortune", _name)

# @cached(ttl=600)
# async def get_single_img(_path: Path, _theme: str, _charac: str) -> None:
#     '''
#         区分图片主题与格式
#     '''
#     _find_url: str = _theme + "/" + _charac
#     return await get_resource(_path, "img", _find_url)

# @cached(ttl=600)
# async def get_theme(_path: Path, _theme: str) -> None:
#     '''
#         区分图片主题与格式
#     '''
#     return await get_resource(_path, "img", _theme)