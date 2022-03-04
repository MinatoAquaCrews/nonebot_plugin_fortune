# import zipfile
# import os

# file_list = os.listdir(os.path.dirname(__file__) + "/resource/img")

# for file_name in file_list:
#     if os.path.splitext(file_name)[1] == '.zip':
#         print(file_name)

#         file_zip = zipfile.ZipFile(file_name, 'r')
#         for file in file_zip.namelist():
#             file_zip.extract(file, r'.')
#         file_zip.close()
#         os.remove(file_name)

# --------------- #
import httpx
from nonebot import logger
from pathlib import Path
from aiocache import cached

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
    print(f"url {url}")
    data = await download(url)
    if data:
        print(f"OK! type: {type(data)}")
    # if data:
    #     with file_path.open("wb") as f:
    #         f.write(data)
            
    # if not file_path.exists():
    #     raise DownloadError
    
    # return file_path.read_bytes()
    return data


def get_font(res_path: Path, name: str) -> bytes:
    return get_resource(res_path, "font", name)

def get_fortune(res_path: Path, name: str) -> bytes:
    return get_resource(res_path, "fortune", name)

def get_theme(res_path: Path, theme: str) -> bytes:
    '''
        区分图片主题与格式
    '''
    return get_resource(res_path, "img", theme)    

import os
import asyncio

def testf(funcname,*args):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(funcname(*args))

if __name__ == "__main__":
    testf(get_fortune, Path(os.path.join(os.path.dirname(__file__), "new")), "copywriting.json")