from typing import Optional, Union, Tuple, List, Dict
from pathlib import Path
import random
try:
    import ujson as json
except ModuleNotFoundError:
    import json

from .config import fortune_config, MainThemeList
from .utils import drawing, MainThemeEnable

class FortuneManager:
    def __init__(self):
        self._user_data: Dict[str, Dict[str, Dict[str, Union[str, bool]]]] = {}
        self._setting: Dict[str, Union[str, Dict[str, List[str]]]] = {}
        self._data_file: Path = fortune_config.fortune_path / "fortune_data.json"
        self._setting_file: Path = fortune_config.fortune_path / "fortune_setting.json"
    
    def _multi_divine_check(self, gid: str, uid: str) -> bool:
        '''
            检测是否重复抽签
        '''
        self._load_data()
        
        return self._user_data[gid][uid]["is_divined"]
    
    def limit_setting_check(self, limit: str) -> Union[bool, str]:
        '''
            检测是否有该特定规则
            检查指定规则的签底所对应主题是否开启或路径是否存在
        '''
        self._load_setting()
        
        if not self._setting["specific_rule"].get(limit):
            return False
        
        spec_path = random.choice(self._setting["specific_rule"][limit])
        for theme in MainThemeList:
            if theme in spec_path:
                return spec_path if MainThemeEnable[theme] else False
        
        return False

    def divine(self, _theme: Optional[str], _spec_path: Optional[str], gid: str, uid: str, nickname: str) -> Tuple[Union[Path, bool], bool]:
        '''
            今日运势抽签
            主题在群设置主题divination__setting()已确认合法
        '''
        self._init_user_data(gid ,uid, nickname)
        
        self._load_setting()
        if not isinstance(_theme, str):
            theme = self._setting["group_rule"][gid]
        else:
            theme = _theme
            
        if not self._multi_divine_check(gid, uid):
            try:
                image_file = drawing(theme, _spec_path, gid, uid)
            except Exception:
                return False, True
            
            self._end_data_handle(gid, uid)
            return image_file, True
        else:
            image_file = fortune_config.fortune_path / "out" / f"{uid}_{gid}.png"
            return image_file, False

    def reset_fortune(self) -> None:
        '''
            重置今日运势并清空图片
        '''
        self._load_data()
        for gid in self._user_data:
            for uid in list(self._user_data[gid]):
                if self._user_data[gid][uid]["is_divined"] == False:
                    self._user_data[gid].pop(uid)
                else:
                    self._user_data[gid][uid]["is_divined"] = False
        
        self._save_data()

        dirPath: Path = fortune_config.fortune_path / "out"
        for pic in dirPath.iterdir():
            pic.unlink()

    def _init_user_data(self, gid: str, uid: str, nickname: str) -> None:
        '''
            初始化用户信息
        '''
        self._load_data()
        self._load_setting()
        
        if "group_rule" not in self._setting:
            self._setting["group_rule"] = {}
        if "specific_rule" not in self._setting:
            self._setting["specific_rule"] = {}
        if gid not in self._setting["group_rule"]:
            self._setting["group_rule"][gid] = "random"
        if gid not in self._user_data:
            self._user_data[gid] = {}
        if uid not in self._user_data[gid]:
            self._user_data[gid][uid] = {
                "uid": uid,
                "gid": gid,
                "nickname": nickname,
                "is_divined": False
            }
        
        self._save_data()
        self._save_setting()

    def get_main_theme_list(self) -> str:
        '''
            获取可设置的抽签主题
        '''
        msg = "可选抽签主题"
        for theme in MainThemeList:
            if theme != "random" and MainThemeEnable[theme] is True:
                msg += f"\n{MainThemeList[theme][0]}"
        
        return msg

    def _end_data_handle(self, gid: str, uid: str) -> None:
        '''
            占卜结束数据保存
        '''
        self._load_data()
        
        self._user_data[gid][uid]["is_divined"] = True
        self._save_data()
    
    def theme_enable_check(self, _theme: str) -> bool:
        '''
            Check whether a theme is enable
        '''
        return True if _theme == "random" or MainThemeEnable.get(_theme, False) else False

    def divination_setting(self, theme: str, gid: str) -> bool:
        '''
            分群管理抽签设置
        '''
        self._load_setting()
        
        if self.theme_enable_check(theme):
            self._setting["group_rule"][gid] = theme
            self._save_setting()
            return True
        
        return False

    def get_setting(self, gid: str) -> str:
        '''
            获取当前群抽签主题，若没有数据则置随机
        '''
        self._load_setting()
        
        if gid not in self._setting["group_rule"]:
            self._setting["group_rule"][gid] = "random"
            self._save_setting()

        return self._setting["group_rule"][gid]
    
    # ------------------------------ Utils ------------------------------ #
    def _load_setting(self) -> None:
        '''
            读取各群抽签设置
        '''
        with open(self._setting_file, 'r', encoding='utf-8') as f:
            self._setting = json.load(f)

    def _save_setting(self) -> None:
        '''
            保存各群抽签设置
        '''
        with open(self._setting_file, 'w', encoding='utf-8') as f:
            json.dump(self._setting, f, ensure_ascii=False, indent=4)
            
    def _load_data(self) -> None:
        '''
            读取抽签数据
        '''
        with open(self._data_file, 'r', encoding='utf-8') as f:
            self._user_data = json.load(f)

    def _save_data(self) -> None:
        '''
            保存抽签数据
        '''
        with open(self._data_file, 'w', encoding='utf-8') as f:
            json.dump(self._user_data, f, ensure_ascii=False, indent=4)

fortune_manager = FortuneManager()

__all__ = [
    fortune_manager
]