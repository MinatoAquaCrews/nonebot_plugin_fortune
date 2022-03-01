from .data_source import PluginConfig
from pathlib import Path
from nonebot import logger
import traceback
from .download import *

class ResourceHandler():
    
    def __init__(self, config: PluginConfig):
        self.res_path: Path = Path(config.fortune_path)
        '''
            抽签主题开关，当随机抽签时判断某主题是否开启
        '''
        self.MainThemeEnable = {
            "pcr":              config.pcr_flag,
            "genshin":          config.genshin_flag,
            "hololive":         config.hololive_flag,
            "touhou":           config.touhou_flag,
            "touhou_old":       config.touhou_olg_flag,
            "touhou_lostword":  config.touhou_lostword,
            "onmyoji":          config.onmyoji_flag,
            "azure":            config.azure_flag,
            "asoul":            config.asoul_flag,
            "arknights":        config.arknights_flag,
            "granblue_fantasy": config.granblue_fantasy_flag,
            "punishing":        config.punishing_flag,
            "pretty_derby":     config.pretty_derby_flag,
            "dc4":              config.dc4_flag,
            "einstein":         config.einstein_flag,
            "sweet_illusion":   config.sweet_illusion_flag,
            "liqingge":         config.liqingge_flag,
            "hoshizora":        config.hoshizora_flag,
            "sakura":           config.sakura_flag
        }
        '''
            抽签主题对应表，第一键值为“抽签设置”或“主题列表”展示的主题名称
            Key-Value: 主题资源文件夹名-设置主题别名
        '''
        self.MainThemeList = {
            "random":   ["随机"],
            "pcr":      ["PCR", "公主链接", "公主连接", "Pcr", "pcr"],
            "genshin":  ["原神", "Genshin Impact", "genshin", "Genshin", "op", "原批"],
            "hololive": ["Hololive", "hololive", "Vtb", "vtb", "管人", "holo", "猴楼"],
            "touhou":   ["东方", "touhou", "Touhou", "车万"],
            "touhou_old": 
                        ["旧东方", "旧版东方", "老东方", "老版东方", "经典东方"],
            "touhou_lostword":
                        ["东方归言录", "东方dlc", "东方DLC", "touhou dlc"],
            "onmyoji":  ["阴阳师", "yys", "Yys", "痒痒鼠"],
            "azure":    ["碧蓝航线", "碧蓝", "azure", "Azure"],
            "asoul":    ["Asoul", "asoul", "a手", "A手", "as", "As"],
            "arknights":["明日方舟", "方舟", "arknights", "鹰角", "Arknights", "舟游"],
            "granblue_fantasy":
                        ["碧蓝幻想", "Granblue Fantasy", "granblue fantasy", "幻想", "fantasy", "Fantasy"],
            "punishing":["战双", "战双帕弥什"],
            "pretty_derby":
                        ["赛马娘", "马", "马娘", "赛马"],
            "dc4":      ["dc4", "DC4", "Dc4", "初音岛", "初音岛4"],
            "einstein": ["爱因斯坦携爱敬上", "爱因斯坦", "einstein", "Einstein"],
            "sweet_illusion":
                        ["灵感满溢的甜蜜创想", "甜蜜一家人", "富婆妹"],
            "liqingge": ["李清歌", "清歌"],
            "hoshizora":["星空列车与白的旅行", "星空列车"],
            "sakura":   ["樱色之云绯色之恋", "樱云之恋", "樱云绯恋", "樱云"]
        }
    
    async def resource_precheck(self):
        '''
            启动时检测字体、文案
        '''
        font_path = self.res_path / "font"
        fortune_path = self.res_path / "fortune"
        font_check = False
        fortune_check = False
        
        if not font_path.exists():
            font_path.parent.mkdir(parents=True, exist_ok=True)
            logger.warning("字体资源不存在，正在下载字体……")
            try:
                await get_font(self.res_path, "Mamelon.otf")
                await get_font(self.res_path, "sakura.ttf")
                font_check = True
            except DownloadError:
                logger.warning(f"字体资源下载出错，请稍后重试！\n{traceback.format_exc()}")
            except:
                logger.warning(f"出错啦，请稍后重试！\n{traceback.format_exc()}")
        else:
            font_check = True
                
        if not fortune_path.exists():
            fortune_path.parent.mkdir(parents=True, exist_ok=True)
            logger.warning("文案资源不存在，正在下载文案……")
            try:
                await get_fortune(self.res_path, "copywriting.json")
                await get_fortune(self.res_path, "goodLuck.json")
                fortune_check = True
            except DownloadError:
                logger.warning(f"文案资源下载出错，请稍后重试！\n{traceback.format_exc()}")
            except:
                logger.warning(f"出错啦，请稍后重试！\n{traceback.format_exc()}")
        else:
            fortune_check = True
        
        return font_check & fortune_check
    
    async def theme_check(self, theme: str):
        image_path = self.res_path / "img"
        theme_path = image_path / theme
        if not image_path.exists():
            image_path.parent.mkdir(parents=True, exist_ok=True)
        if not theme_path.exists():
            theme_path.parent.mkdir(parents=True, exist_ok=True)
            logger.warning(f"主题 {self.MainThemeList[theme][0]} 图片资源不存在，正在下载图片……")
            try:
                await get_theme(self.res_path, "copywriting.json")
            except DownloadError:
                logger.warning(f"文案资源下载出错，请稍后重试！\n{traceback.format_exc()}")
            except:
                logger.warning(f"出错啦，请稍后重试！\n{traceback.format_exc()}")