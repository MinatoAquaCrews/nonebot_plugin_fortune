import json
import random
from datetime import date, datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from .config import DateTimeEncoder, FortuneThemesDict, fortune_config
from .utils import drawing, theme_flag_check


class FortuneManager:
    def __init__(self):
        self._user_data: Dict[str, Dict[str, Dict[str, Union[str, int, date]]]] = dict()
        self._group_rules: Dict[str, str] = dict()
        self._specific_rules: Dict[str, List[str]] = dict()
        self._user_data_file: Path = fortune_config.fortune_path / "fortune_data.json"
        self._group_rules_file: Path = fortune_config.fortune_path / "group_rules.json"
        self._specific_rules_file: Path = (
            fortune_config.fortune_path / "specific_rules.json"
        )

    def _multi_divine_check(self, gid: str, uid: str, nowtime: date) -> bool:
        """
        检测是否重复抽签：判断此时与上次签到时间是否为同一天（年、月、日均相同）
        """
        self._load_data()

        # Means this is a new user
        if isinstance(self._user_data[gid][uid]["last_sign_date"], int):
            return False

        last_sign_date: datetime = datetime.strptime(
            # type: ignore
            self._user_data[gid][uid]["last_sign_date"],
            "%Y-%m-%d",
        )

        return last_sign_date.date() == nowtime

    def specific_check(self, charac: str) -> Optional[str]:
        """
        检测是否有该签底规则
        检查指定规则的签底所对应主题是否开启或路径是否存在
        """
        self._load_specific_rules()

        if not self._specific_rules.get(charac, False):
            return None

        spec_path: str = random.choice(self._specific_rules[charac])
        for theme in FortuneThemesDict:
            if theme in spec_path:
                return spec_path if theme_flag_check(theme) else None

        return None

    def divine(
        self,
        gid: str,
        uid: str,
        _theme: Optional[str] = None,
        spec_path: Optional[str] = None,
    ) -> Tuple[bool, Optional[Path]]:
        """
        今日运势抽签，主题已确认合法
        """
        now_time: date = date.today()

        self._init_user_data(gid, uid)
        self._load_group_rules()

        if not isinstance(_theme, str):
            theme: str = self._group_rules[gid]
        else:
            theme: str = _theme

        if not self._multi_divine_check(gid, uid, now_time):
            try:
                img_path = drawing(gid, uid, theme, spec_path)
            except Exception:
                return True, None

            # Record the sign-in time
            self._end_data_handle(gid, uid, now_time)
            return True, img_path
        else:
            img_path: Path = fortune_config.fortune_path / "out" / f"{gid}_{uid}.png"
            return False, img_path

    @staticmethod
    def clean_out_pics() -> None:
        """
        Clean all the pictures saved at yesterday.
        """
        dirPath: Path = fortune_config.fortune_path / "out"
        for pic in dirPath.iterdir():
            pic.unlink()

    def _init_user_data(self, gid: str, uid: str) -> None:
        """
        初始化用户信息：
        1. 群聊不在群组规则内，初始化
        2. 群聊不在抽签数据内，初始化
        3. 用户不在抽签数据内，初始化
        """
        self._load_data()
        self._load_group_rules()

        if gid not in self._group_rules:
            self._group_rules.update({gid: "random"})

        if gid not in self._user_data:
            self._user_data[gid] = {}

        if uid not in self._user_data[gid]:
            self._user_data[gid][uid] = {
                "last_sign_date": 0  # Last sign-in date. YY-MM-DD
            }

        self._save_data()
        self._save_group_rules()

    @staticmethod
    def get_available_themes() -> str:
        """
        获取可设置的抽签主题
        """
        msg: str = "可选抽签主题"
        for theme in FortuneThemesDict:
            if theme != "random" and theme_flag_check(theme):
                msg += f"\n{FortuneThemesDict[theme][0]}"

        return msg

    def _end_data_handle(self, gid: str, uid: str, nowtime: date) -> None:
        """
        占卜结束数据保存
        """
        self._load_data()

        self._user_data[gid][uid]["last_sign_date"] = nowtime
        self._save_data()

    @staticmethod
    def theme_enable_check(_theme: str) -> bool:
        """
        Check whether a theme is enable
        """
        return _theme == "random" or theme_flag_check(_theme)

    def divination_setting(self, theme: str, gid: str) -> bool:
        """
        分群管理抽签设置
        """
        self._load_group_rules()

        if self.theme_enable_check(theme):
            self._group_rules[gid] = theme
            self._save_group_rules()
            return True

        return False

    def get_group_theme(self, gid: str) -> str:
        """
        获取当前群抽签主题，若没有数据则初始化为随机
        """
        self._load_group_rules()

        if gid not in self._group_rules:
            self._group_rules.update({gid: "random"})
            self._save_group_rules()

        return self._group_rules[gid]

    # ------------------------------ Utils ------------------------------ #
    def _load_data(self) -> None:
        """
        读取抽签数据
        """
        with open(self._user_data_file, "r", encoding="utf-8") as f:
            self._user_data = json.load(f)

    def _save_data(self) -> None:
        """
        保存抽签数据
        """
        with open(self._user_data_file, "w", encoding="utf-8") as f:
            json.dump(
                self._user_data, f, ensure_ascii=False, indent=4, cls=DateTimeEncoder
            )

    def _load_group_rules(self) -> None:
        """
        读取各群抽签主题设置
        """
        with open(self._group_rules_file, "r", encoding="utf-8") as f:
            self._group_rules = json.load(f)

    def _save_group_rules(self) -> None:
        """
        保存各群抽签主题设置
        """
        with open(self._group_rules_file, "w", encoding="utf-8") as f:
            json.dump(self._group_rules, f, ensure_ascii=False, indent=4)

    def _load_specific_rules(self) -> None:
        """
        读取签底指定规则 READ ONLY
        """
        with open(self._specific_rules_file, "r", encoding="utf-8") as f:
            self._specific_rules = json.load(f)


fortune_manager = FortuneManager()
