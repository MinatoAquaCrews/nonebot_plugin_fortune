from nonebot.adapters.onebot.v11 import GroupMessageEvent
from typing import Optional, Union, Dict, Tuple
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
        self.user_data = {}
        self.setting = {}
        _path: Path = fortune_config.fortune_path

        if not _path.exists():
            _path.mkdir(parents=True, exist_ok=True)
            
        data_file = _path / "fortune_data.json"
        setting_file = _path / "fortune_setting.json"

        self.data_file = data_file
        self.setting_file = setting_file
        
        if not data_file.exists():
            with open(data_file, "w", encoding="utf-8") as f:
                f.write(json.dumps(dict()))

        if data_file.exists():
            with open(data_file, "r", encoding="utf-8") as f:
                self.user_data = json.load(f)
        
        if not setting_file.exists():
            with open(setting_file, "w", encoding="utf-8") as f:
                f.write(json.dumps(dict()))
        
        if setting_file.exists():
            with open(setting_file, "r", encoding="utf-8") as f:
                self.setting = json.load(f)
    
    def _multi_divine_check(self, event: GroupMessageEvent) -> bool:
        '''
            检测是否重复抽签
        '''
        return self.user_data[str(event.group_id)][str(event.user_id)]["is_divined"]
    
    def limit_setting_check(self, limit: str) -> Union[bool, str]:
        '''
            检测是否有该特定规则
            检查指定规则的签底所对应主题是否开启
            或路径是否存在
        '''
        if not self.setting["specific_rule"].get(limit):
            return False
        
        spec_path = random.choice(self.setting["specific_rule"][limit])
        for theme in MainThemeList:
            if theme in spec_path:
                return spec_path if MainThemeEnable[theme] else False
        
        return False

    def divine(self, _theme: Optional[str], _spec_path: Optional[str], event: GroupMessageEvent) -> Tuple[str, bool]:
        '''
            今日运势抽签
            主题在群设置主题divination_setting()已确认合法
        '''
        self._init_user_data(event)
        group_id = str(event.group_id)
        user_id = str(event.user_id)
        
        if not isinstance(_theme, str):
            theme = self.setting["group_rule"][group_id]
        else:
            theme = _theme
            
        if not self._multi_divine_check(event):
            image_file = drawing(theme, _spec_path, user_id, group_id)
            self._end_data_handle(event)
            return image_file, True
        else:
            image_file = fortune_config.fortune_path / "out" / f"{user_id}_{group_id}.png"
            return image_file, False

    def reset_fortune(self) -> None:
        '''
            重置今日运势并清空图片
        '''
        for group_id in self.user_data:
            for user_id in list(self.user_data[group_id]):
                if self.user_data[group_id][user_id]["is_divined"] == False:
                    self.user_data[group_id].pop(user_id)
                else:
                    self.user_data[group_id][user_id]["img_path"] = ""
                    self.user_data[group_id][user_id]["is_divined"] = False
        
        self._save_data()

        dirPath: Path = fortune_config.fortune_path / "out"
        for pic in dirPath.iterdir():
            pic.unlink()

    def _init_user_data(self, event: GroupMessageEvent) -> None:
        '''
            初始化用户信息
        '''
        user_id = str(event.user_id)
        group_id = str(event.group_id)
        nickname = event.sender.card if event.sender.card else event.sender.nickname
        
        if "group_rule" not in self.setting:
            self.setting["group_rule"] = {}
        if "specific_rule" not in self.setting:
            self.setting["specific_rule"] = {}
        if group_id not in self.setting["group_rule"]:
            self.setting["group_rule"][group_id] = "random"
        if group_id not in self.user_data:
            self.user_data[group_id] = {}
        if user_id not in self.user_data[group_id]:
            self.user_data[group_id][user_id] = {
                "user_id": user_id,
                "group_id": group_id,
                "nickname": nickname,
                "is_divined": False
            }

    def get_main_theme_list(self) -> str:
        '''
            获取可设置的抽签主题
        '''
        msg = "可选抽签主题"
        for theme in MainThemeList:
            if theme != "random" and MainThemeEnable[theme] is True:
                msg += f"\n{MainThemeList[theme][0]}"
        
        return msg
    
    def get_user_data(self, event: GroupMessageEvent) -> Dict[str, Union[str, bool]]:
        '''
            获取用户数据
        '''
        self._init_user_data(event)
        return self.user_data[str(event.group_id)][str(event.user_id)]

    def _end_data_handle(self, event: GroupMessageEvent) -> None:
        '''
            占卜结束数据保存
        '''
        user_id = str(event.user_id)
        group_id = str(event.group_id)
        self.user_data[group_id][user_id]["is_divined"] = True
        self._save_data()
    
    def theme_enable_check(self, _theme: str) -> bool:
        '''
            Check whether a theme is enable
        '''
        return True if _theme == "random" or MainThemeEnable.get(_theme) else False

    def divination_setting(self, theme: str, event: GroupMessageEvent) -> bool:
        '''
            分群管理抽签设置
        '''
        group_id = str(event.group_id)
        
        if self.theme_enable_check(theme):
            self.setting["group_rule"][group_id] = theme
            self._save_setting()
            return True
        
        return False

    def get_setting(self, event: GroupMessageEvent) -> str:
        '''
            获取当前群抽签主题，若没有数据则置随机
        '''
        group_id = str(event.group_id)
        if group_id not in self.setting["group_rule"]:
            self.setting["group_rule"][group_id] = "random"
            self._save_setting()

        return self.setting["group_rule"][group_id]
    
    # ------------------------------ Utils ------------------------------ #
    def _load_setting(self) -> None:
        '''
            读取各群抽签设置
        '''
        with open(self.setting_file, 'r', encoding='utf-8') as f:
            self.setting = json.load(f)

    def _save_setting(self) -> None:
        '''
            保存各群抽签设置
        '''
        with open(self.setting_file, 'w', encoding='utf-8') as f:
            json.dump(self.setting, f, ensure_ascii=False, indent=4)
            
    def _load_data(self) -> None:
        '''
            读取抽签数据
        '''
        with open(self.data_file, 'r', encoding='utf-8') as f:
            self.user_data = json.load(f)

    def _save_data(self) -> None:
        '''
            保存抽签数据
        '''
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.user_data, f, ensure_ascii=False, indent=4)

fortune_manager = FortuneManager()