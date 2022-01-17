from nonebot.adapters.cqhttp import GroupMessageEvent, MessageSegment, Bot
from typing import Optional, Union, List, Dict
import nonebot
import os

try:
    import ujson as json
except ModuleNotFoundError:
    import json

_FORTUNE_PATH = nonebot.get_driver().config.fortune_path
DEFAULT_PATH = os.path.join(os.path.dirname(__file__), "resource")
FORTUNE_PATH = DEFAULT_PATH if not _FORTUNE_PATH else _FORTUNE_PATH

from .utils import MainTheme, drawing

class FortuneManager:
    def __init__(self, file: Optional[str]):
        self.user_data = {}
        self.main_theme = MainTheme.RANDOM
        if not file:
            file = os.path.join(FORTUNE_PATH, "fortune_data.json")
        
        self.file = file
        if file.exists():
            with open(file, "r", encoding="utf-8") as f:
                self.user_data = json.load(f)
 
    def divine(self, specific_limit, event: GroupMessageEvent):
        '''
            今日运势占卜
        '''
        self._init_user_data(event)
        msg = []
        if self.user_data[str(event.group_id)][str(event.user_id)]["is_divined"]:
            image_file = self.user_data[str(event.group_id)][str(event.user_id)]["img_path"]
            return image_file, False
                
        image_file = drawing(self.main_theme, specific_limit, event.user_id, event.group_id)
        self._end_data_handle(event.user_id, event.group_id, image_file)
        return image_file, True

    def reset_fortune(self):
        '''
            重置今日运势
        '''
        for group in self.user_data.keys():
            for user_id in self.user_data[group].keys():
                self.user_data[group][user_id]["img_path"] = ""
                self.user_data[group][user_id]["is_divined"] = False
        
        self.save()

    def save(self):
        '''
            保存数据
        '''
        with open(self.file, 'w', encoding='utf-8') as f:
            json.dump(self.user_data, f, ensure_ascii=False, indent=4)

    def _init_user_data(self, event: GroupMessageEvent):
        '''
            初始化用户信息
        '''
        user_id = str(event.user_id)
        group_id = str(event.group_id)
        nickname = event.sender.card if event.sender.card else event.sender.nickname
        if group_id not in self.user_data.keys():
            self.user_data[group_id] = {}
        if user_id not in self.user_data[group_id].keys():
            self.user_data[group_id][user_id] = {
                "user_id": user_id,
                "group_id": group_id,
                "nickname": nickname,
                "img_path": "",
                "is_divined": False
            }
    
    def get_user_data(self, event: GroupMessageEvent) -> Dict[str, Union[str, int]]:
        """
            获取用户数据
        """
        self._init_user_data(event)
        return self.user_data[str(event.group_id)][str(event.user_id)]

    def _end_data_handle(
        self,
        user_id: int,
        group_id: int,
        img_path: str,
    ):
        """
            占卜结束数据保存
        """
        user_id = str(user_id)
        group_id = str(group_id)
        self.user_data[group_id][user_id]["img_path"] = img_path
        self.user_data[group_id][user_id]["is_divined"] = True
        self.save()