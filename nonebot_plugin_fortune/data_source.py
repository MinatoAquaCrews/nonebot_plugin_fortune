from typing import Optional, Union, Tuple, List, Dict
from pathlib import Path
import random
try:
    import ujson as json
except ModuleNotFoundError:
    import json

from .config import fortune_config, FortuneThemesDict
from .utils import drawing, themes_flag_check

class FortuneManager:
    
    def __init__(self):
        self._user_data: Dict[str, Dict[str, Dict[str, Union[str, bool]]]] = dict()
        self._group_rules: Dict[str, str] = dict()
        self._specific_rules: Dict[str, List[str]] = dict()
        self._user_data_file: Path = fortune_config.fortune_path / "fortune_data.json"
        self._group_rules_file: Path = fortune_config.fortune_path / "group_rules.json"
        self._specific_rules_file: Path = fortune_config.fortune_path / "specific_rules.json"
    
    def _multi_divine_check(self, gid: str, uid: str) -> bool:
        '''
            检测是否重复抽签
        '''
        self._load_data()
        
        return self._user_data[gid][uid]["is_divined"]
    
    def specific_check(self, charac: str) -> Union[str, None]:
        '''
            检测是否有该签底规则
            检查指定规则的签底所对应主题是否开启或路径是否存在
        '''
        self._load_specific_rules()
        
        if not self._specific_rules.get(charac, False):
            return None
        
        spec_path: str = random.choice(self._specific_rules[charac])
        for theme in FortuneThemesDict:
            if theme in spec_path:
                return spec_path if themes_flag_check(theme) else None
        
        return None

    def divine(self, gid: str, uid: str, nickname: str, _theme: Optional[str] = None, spec_path: Optional[str] = None) -> Tuple[bool, Union[Path, None]]:
        '''
            今日运势抽签，主题已确认合法
        '''
        self._init_user_data(gid ,uid, nickname)
        self._load_group_rules()
        
        if not isinstance(_theme, str):
            theme: str = self._group_rules[gid]
        else:
            theme: str = _theme
            
        if not self._multi_divine_check(gid, uid):
            try:
                image_file = drawing(gid, uid, theme, spec_path)
            except Exception:
                return True, None
            
            self._end_data_handle(gid, uid)
            return True, image_file
        else:
            image_file: Path = fortune_config.fortune_path / "out" / f"{gid}_{uid}.png"
            return False, image_file

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
            初始化用户信息：
            - 群聊不在群组规则内，初始化
            - 群聊不在抽签数据内，初始化
            - 用户不在抽签数据内，初始化
        '''
        self._load_data()
        self._load_group_rules()
        
        if gid not in self._group_rules:
            self._group_rules.update({gid: "random"})
        
        if gid not in self._user_data:
            self._user_data[gid] = {}
        
        if uid not in self._user_data[gid]:
            self._user_data[gid][uid] = {
                "gid": gid,
                "uid": uid,
                "nickname": nickname,
                "is_divined": False
            }
        
        self._save_data()
        self._save_group_rules()

    def get_main_theme_list(self) -> str:
        '''
            获取可设置的抽签主题
        '''
        msg: str = "可选抽签主题"
        for theme in FortuneThemesDict:
            if theme != "random" and themes_flag_check(theme):
                msg += f"\n{FortuneThemesDict[theme][0]}"
        
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
        return _theme == "random" or themes_flag_check(_theme)

    def divination_setting(self, theme: str, gid: str) -> bool:
        '''
            分群管理抽签设置
        '''
        self._load_group_rules()
        
        if self.theme_enable_check(theme):
            self._group_rules[gid] = theme
            self._save_group_rules()
            return True
        
        return False

    def get_group_theme(self, gid: str) -> str:
        '''
            获取当前群抽签主题，若没有数据则置随机
        '''
        self._load_group_rules()
        
        if gid not in self._group_rules:
            self._group_rules.update({gid: "random"})
            self._save_group_rules()

        return self._group_rules[gid]
    
    # ------------------------------ Utils ------------------------------ #            
    def _load_data(self) -> None:
        '''
            读取抽签数据
        '''
        with open(self._user_data_file, "r", encoding="utf-8") as f:
            self._user_data = json.load(f)

    def _save_data(self) -> None:
        '''
            保存抽签数据
        '''
        with open(self._user_data_file, "w", encoding="utf-8") as f:
            json.dump(self._user_data, f, ensure_ascii=False, indent=4)
    
    def _load_group_rules(self) -> None:
        '''
            读取各群抽签主题设置
        '''
        with open(self._group_rules_file, "r", encoding="utf-8") as f:
            self._group_rules = json.load(f)

    def _save_group_rules(self) -> None:
        '''
            保存各群抽签主题设置
        '''
        with open(self._group_rules_file, "w", encoding="utf-8") as f:
            json.dump(self._group_rules, f, ensure_ascii=False, indent=4)
    
    def _load_specific_rules(self) -> None:
        '''
            读取签底指定规则 READ ONLY
        '''
        with open(self._specific_rules_file, "r", encoding="utf-8") as f:
            self._specific_rules = json.load(f)

fortune_manager = FortuneManager()