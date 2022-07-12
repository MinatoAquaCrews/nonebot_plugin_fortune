from nonebot import get_driver, logger
from pydantic import BaseModel, Extra, ValidationError
from typing import List, Dict
from pathlib import Path
try:
    import ujson as json
except ModuleNotFoundError:
    import json

'''
    抽签主题对应表，第一键值为“抽签设置”或“主题列表”展示的主题名称
    Key-Value: 主题资源文件夹名-设置主题别名
'''
MainThemeList: Dict[str, List[str]] = {
    "random": ["随机"],
    "pcr": ["PCR", "公主链接", "公主连结", "Pcr", "pcr"],
    "genshin": ["原神", "Genshin Impact", "genshin", "Genshin", "op", "原批"],
    "hololive": ["Hololive", "hololive", "Vtb", "vtb", "管人", "holo", "猴楼"],
    "touhou": ["东方", "touhou", "Touhou", "车万"],
    "touhou_lostword": ["东方归言录", "东方lostword", "touhou lostword", "Touhou dlc"],
    "touhou_old": ["旧东方", "旧版东方", "老东方", "老版东方", "经典东方"],
    "onmyoji": ["阴阳师", "yys", "Yys", "痒痒鼠"],
    "azure": ["碧蓝航线", "碧蓝", "azure", "Azure"],
    "asoul": ["Asoul", "asoul", "a手", "A手", "as", "As"],
    "arknights": ["明日方舟", "方舟", "arknights", "鹰角", "Arknights", "舟游"],
    "granblue_fantasy": ["碧蓝幻想", "Granblue Fantasy", "granblue fantasy", "幻想", "fantasy", "Fantasy"],
    "punishing":["战双", "战双帕弥什"],
    "pretty_derby": ["赛马娘", "马", "马娘", "赛马"],
    "dc4": ["dc4", "DC4", "Dc4", "初音岛", "初音岛4"],
    "einstein": ["爱因斯坦携爱敬上", "爱因斯坦", "einstein", "Einstein"],
    "sweet_illusion": ["灵感满溢的甜蜜创想", "甜蜜一家人", "富婆妹"],
    "liqingge": ["李清歌", "清歌"],
    "hoshizora": ["星空列车与白的旅行", "星空列车"],
    "sakura": ["樱色之云绯色之恋", "樱云之恋", "樱云绯恋", "樱云"],
    "summer_pockets": ["夏日口袋", "夏兜", "sp", "SP"],
    "amazing_grace": ["奇异恩典"]
}

class PluginConfig(BaseModel, extra=Extra.ignore):
    fortune_path: Path = Path(__file__).parent / "resource"
    '''
        各主题抽签开关，仅在random抽签中生效
        请确保不全是False
    '''
    amazing_grace_flag: bool = True
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
    summer_pockets_flag: bool = True

driver = get_driver()
fortune_config: PluginConfig = PluginConfig.parse_obj(driver.config.dict())

'''
    Reserved for next version
'''
@driver.on_startup
async def check_config() -> None:
    config_path: Path = fortune_config.fortune_path / "fortune_config.json"
    
    if not config_path.exists():
        logger.warning("配置文件不存在，已重新生成配置文件……")
        config = PluginConfig()
    else:
        with config_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        try:
            config = PluginConfig.parse_obj({**driver.config.dict(), **data})
        except ValidationError:
            config = PluginConfig()
            logger.warning("配置文件格式错误，已重新生成配置文件……")
                
    with config_path.open("w", encoding="utf-8") as f:
        content = config.dict()
        # Posix path need to transfer to str then write in json
        content.update({"fortune_path": str(content.get("fortune_path"))})
        json.dump(content, f, ensure_ascii=False, indent=4)