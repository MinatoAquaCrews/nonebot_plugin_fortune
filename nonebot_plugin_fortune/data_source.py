from nonebot.adapters.cqhttp import GroupMessageEvent
from typing import Optional, Union, Dict
from pathlib import Path
import os
import nonebot

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
        self.main_theme = "random"
        if not file:
            file = Path(FORTUNE_PATH) / "fortune_data.json"
        
        self.file = file
        if file.exists():
            with open(file, "r", encoding="utf-8") as f:
                self.user_data = json.load(f)

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
        if not self.check(event):
            image_file = drawing(self.main_theme, limit, event.user_id, event.group_id)
            self._end_data_handle(event)
            return image_file, True
        else:
            image_file = Path(FORTUNE_PATH) / "out" / f"{str(event.user_id)}_{str(event.group_id)}.png"
            return image_file, False

    def reset_fortune(self):
        '''
            重置今日运势并清空图片
        '''
        for group in self.user_data.keys():
            for user_id in self.user_data[group].keys():
                self.user_data[group][user_id]["img_path"] = ""
                self.user_data[group][user_id]["is_divined"] = False
        
        dirPath = Path(f"{FORTUNE_PATH}/out")
        self.save()

        for pic in dirPath.iterdir:
            pic.unlink()

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
                "is_divined": False
            }
    
    def get_user_data(self, event: GroupMessageEvent) -> Dict[str, Union[str, Path, bool]]:
        """
            获取用户数据
        """
        self._init_user_data(event)
        return self.user_data[str(event.group_id)][str(event.user_id)]

    def _end_data_handle(self, event: GroupMessageEvent):
        """
            占卜结束数据保存
        """
        user_id = str(event.user_id)
        group_id = str(event.group_id)
        self.user_data[group_id][user_id]["is_divined"] = True
        self.save()

fortune_manager = FortuneManager(Path(FORTUNE_PATH) / "fortune_data.json")