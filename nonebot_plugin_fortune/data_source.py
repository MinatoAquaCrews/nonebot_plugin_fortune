from nonebot.adapters.onebot.v11 import GroupMessageEvent
from typing import Optional, Union, Dict
from pathlib import Path
import nonebot
import os

try:
    import ujson as json
except ModuleNotFoundError:
    import json

_FORTUNE_PATH = nonebot.get_driver().config.fortune_path
DEFAULT_PATH = os.path.join(os.path.dirname(__file__), "resource")
FORTUNE_PATH = DEFAULT_PATH if not _FORTUNE_PATH else _FORTUNE_PATH

from .utils import drawing

class FortuneManager:
    def __init__(self, file: Optional[Path]):
        self.user_data = {}
        self.setting = {}
        if not file:
            data_file = Path(FORTUNE_PATH) / "fortune_data.json"
            setting_file = Path(FORTUNE_PATH) / "fortune_setting.json"
        else:
            data_file = file / "fortune_data.json"
            setting_file = file / "fortune_setting.json"

        self.data_file = data_file
        self.setting_file = setting_file
        if data_file.exists():
            with open(data_file, "r", encoding="utf-8") as f:
                self.user_data = json.load(f)
        
        if setting_file.exists():
            with open(setting_file, "r", encoding="utf-8") as f:
                self.setting = json.load(f)

    def check(self, event: GroupMessageEvent) -> bool:
        '''
            检测是否重复抽签
        '''
        return self.user_data[str(event.group_id)][str(event.user_id)]["is_divined"]

    def divine(self, limit: Optional[str], event: GroupMessageEvent) -> tuple[str, bool]:
        '''
            今日运势抽签
        '''
        self._init_user_data(event)
        theme = self.setting[str(event.group_id)]

        if not self.check(event):
            image_file = drawing(theme, limit, event.user_id, event.group_id)
            self._end_data_handle(event)
            return image_file, True
        else:
            image_file = Path(FORTUNE_PATH) / "out" / f"{str(event.user_id)}_{str(event.group_id)}.png"
            return image_file, False

    def reset_fortune(self) -> None:
        '''
            重置今日运势并清空图片
        '''
        for group in self.user_data.keys():
            for user_id in self.user_data[group].keys():
                self.user_data[group][user_id]["img_path"] = ""
                self.user_data[group][user_id]["is_divined"] = False
        
        self.save()

        dirPath = Path(FORTUNE_PATH) / "out"
        for pic in dirPath.iterdir():
            pic.unlink()

    def save_data(self) -> None:
        '''
            保存抽签数据
        '''
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.user_data, f, ensure_ascii=False, indent=4)

    def _init_user_data(self, event: GroupMessageEvent) -> None:
        '''
            初始化用户信息
        '''
        user_id = str(event.user_id)
        group_id = str(event.group_id)
        nickname = event.sender.card if event.sender.card else event.sender.nickname
        
        if group_id not in self.setting.keys():
            self.setting[group_id] = "random"
        if group_id not in self.user_data.keys():
            self.user_data[group_id] = {}
        if user_id not in self.user_data[group_id].keys():
            self.user_data[group_id][user_id] = {
                "user_id": user_id,
                "group_id": group_id,
                "nickname": nickname,
                "is_divined": False
            }
    
    def get_user_data(self, event: GroupMessageEvent) -> Dict[str, Union[str, bool]]:
        """
            获取用户数据
        """
        self._init_user_data(event)
        return self.user_data[str(event.group_id)][str(event.user_id)]

    def _end_data_handle(self, event: GroupMessageEvent) -> None:
        """
            占卜结束数据保存
        """
        user_id = str(event.user_id)
        group_id = str(event.group_id)
        self.user_data[group_id][user_id]["is_divined"] = True
        self.save_data()
        self.save_setting()

    def divination_setting(self, theme: str, event: GroupMessageEvent) -> None:
        '''
            分群管理抽签设置
        '''
        group_id = str(event.group_id)
        self.setting[group_id] = theme
        self.save_setting()

    def get_setting(self, event: GroupMessageEvent) -> str:
        group_id = str(event.group_id)
        if group_id not in self.setting.keys():
            self.setting[group_id] = "random"
            self.save_setting()

        return self.setting[group_id]

    def save_setting(self) -> None:
        '''
            保存各群抽签设置
        '''
        with open(self.setting_file, 'w', encoding='utf-8') as f:
            json.dump(self.setting, f, ensure_ascii=False, indent=4)

fortune_manager = FortuneManager(Path(FORTUNE_PATH))