import nonebot
from nonebot import logger
import os
from pathlib import Path
from pydantic import BaseModel, ValidationError
try:
    import ujson as json
except ModuleNotFoundError:
    import json

class PluginConfig(BaseModel):
    fortune_path: str = os.path.join(os.path.dirname(__file__), "resource")
    '''
        各主题抽签开关，仅在random抽签中生效
        请确保不全是False
    '''
    arknights_flag: bool = True
    asoul_flag: bool = True
    azure_flag: bool = True
    genshin_flag:  bool = True
    onmyoji_flag: bool = True
    pcr_flag: bool = True
    touhou_flag: bool = True
    touhou_lostword_flag: bool = True
    touhou_olg_flag: bool = True
    hololive_flag: bool = True
    granblue_fantasy_flag: bool = True
    punishing_flag: bool = True
    pretty_derby_flag: bool = True
    dc4_flag: bool = True
    einstein_flag: bool = True
    sweet_illusion_flag: bool = True
    liqingge_flag: bool = True
    hoshizora_flag: bool = True
    sakura_flag: bool = True 

driver = nonebot.get_driver()
global_config = driver.config
config: PluginConfig = PluginConfig.parse_obj(global_config.dict())
FORTUNE_PATH: str = config.fortune_path
CONFIG_PATH: Path = Path(FORTUNE_PATH) / "fortune_config.json"

'''
    Reserved for next version
'''
@driver.on_startup
async def check_config():
    if not CONFIG_PATH.exists():
        logger.warning("配置文件不存在，已重新生成配置文件……")
        config = PluginConfig()
    else:
        with CONFIG_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
        try:
            config = PluginConfig.parse_obj({**global_config.dict(), **data})
        except ValidationError:
            config = PluginConfig()
            logger.warning("配置文件格式错误，已重新生成配置文件……")
        
    with CONFIG_PATH.open("w", encoding="utf-8") as f:
        json.dump(config.dict(), f, ensure_ascii=False, indent=4)