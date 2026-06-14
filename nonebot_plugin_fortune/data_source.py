import asyncio
import json
from datetime import date, datetime
from pathlib import Path
from random import choice
from typing import Any, Dict, List, Optional, Tuple, Union

from nonebot.log import logger

from .config import (
    GROUP_RULES_FILE,
    OUT_DIR,
    SPECIFIC_RULES_FILE,
    USER_DATA_FILE,
    DateTimeEncoder,
    FortuneThemesDict,
)
from .utils import drawing, theme_flag_check


class FortuneManager:
    """
    抽签数据管理
    首次访问时一次性载入内存，只在发生变更时落盘
    涉及共享数据的操作都通过 ``_lock``串行，避免覆盖导致记录丢失
    """

    def __init__(self):
        self._user_data: Dict[str, Dict[str, Dict[str, Union[str, int, date]]]] = dict()
        self._group_rules: Dict[str, str] = dict()
        self._specific_rules: Dict[str, List[str]] = dict()
        self._user_data_file: Path = USER_DATA_FILE
        self._group_rules_file: Path = GROUP_RULES_FILE
        self._specific_rules_file: Path = SPECIFIC_RULES_FILE
        self._lock = asyncio.Lock()
        self._loaded: bool = False

    def _multi_divine_check(self, gid: str, uid: str, nowtime: date) -> bool:
        """
        检测是否重复抽签
        """
        last = self._user_data[gid][uid]["last_sign_date"]

        if isinstance(last, int):
            return False

        if isinstance(last, date):
            last_sign_date: date = last
        else:
            last_sign_date = datetime.strptime(last, "%Y-%m-%d").date()

        return last_sign_date == nowtime

    async def specific_check(self, charac: str) -> Optional[str]:
        """
        检测是否有该签底规则，并检查其所属主题是否开启
        """
        async with self._lock:
            self._ensure_loaded()
            paths = self._specific_rules.get(charac)
            if not paths:
                return None

            spec_path: str = choice(paths)
            theme: str = Path(spec_path).parts[0]
            return spec_path if theme_flag_check(theme) else None

    # 抽签主流程
    async def divine(
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
        out_path: Path = OUT_DIR / f"{gid}_{uid}.png"

        async with self._lock:
            self._ensure_loaded()
            self._init_user_data(gid, uid)

            theme: str = _theme if isinstance(_theme, str) else self._group_rules[gid]
            already_divined: bool = self._multi_divine_check(gid, uid, now_time)

            if already_divined:
                if out_path.exists():
                    return False, out_path

                img_path = await self._safe_draw(gid, uid, theme, spec_path)
                return False, img_path

            img_path = await self._safe_draw(gid, uid, theme, spec_path)
            if img_path is None:
                return True, None

            # 绘制成功后记录签到时间
            self._user_data[gid][uid]["last_sign_date"] = now_time
            self._save_data()
            return True, img_path

    @staticmethod
    def clean_out_pics() -> None:
        """
        清空缓存目录下昨日生成的图片
        """
        if not OUT_DIR.exists():
            return

        for pic in OUT_DIR.iterdir():
            pic.unlink()

    def _init_user_data(self, gid: str, uid: str) -> None:
        """
        确保群组与用户在内存数据中存在；新建的部分立即落盘。
        调用前需持有 ``_lock`` 且数据已载入。
        """
        dirty_rules = False
        if gid not in self._group_rules:
            self._group_rules[gid] = "random"
            dirty_rules = True

        dirty_data = False
        if gid not in self._user_data:
            self._user_data[gid] = {}
            dirty_data = True

        if uid not in self._user_data[gid]:
            self._user_data[gid][uid] = {"last_sign_date": 0}
            dirty_data = True

        if dirty_rules:
            self._save_group_rules()
        if dirty_data:
            self._save_data()

    async def _safe_draw(
        self, gid: str, uid: str, theme: str, spec_path: Optional[str]
    ) -> Optional[Path]:
        """线程池绘图，失败时记录日志并返回 None"""
        try:
            return await asyncio.to_thread(drawing, gid, uid, theme, spec_path)
        except Exception:
            logger.exception(
                f"绘制运势图失败 | Group {gid} | User {uid} | theme={theme} | spec={spec_path}"
            )
            return None

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

    @staticmethod
    def theme_enable_check(_theme: str) -> bool:
        """
        检查某主题是否启用
        """
        return _theme == "random" or theme_flag_check(_theme)

    async def divination_setting(self, theme: str, gid: str) -> bool:
        """
        分群管理抽签设置
        """
        async with self._lock:
            self._ensure_loaded()
            if self.theme_enable_check(theme):
                self._group_rules[gid] = theme
                self._save_group_rules()
                return True

            return False

    async def get_group_theme(self, gid: str) -> str:
        """
        获取当前群抽签主题，若没有数据则初始化为随机
        """
        async with self._lock:
            self._ensure_loaded()
            if gid not in self._group_rules:
                self._group_rules[gid] = "random"
                self._save_group_rules()

            return self._group_rules[gid]

    # 内部数据操作
    def _ensure_loaded(self) -> None:
        """
        首次访问时把磁盘数据载入内存
        需持有 _lock
        """
        if self._loaded:
            return

        self._user_data = self._read_json(self._user_data_file)
        self._group_rules = self._read_json(self._group_rules_file)
        self._specific_rules = self._read_json(self._specific_rules_file)
        self._loaded = True

    @staticmethod
    def _read_json(path: Path) -> Dict[str, Any]:
        if not path.exists():
            return dict()
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_data(self) -> None:
        with open(self._user_data_file, "w", encoding="utf-8") as f:
            json.dump(
                self._user_data, f, ensure_ascii=False, indent=4, cls=DateTimeEncoder
            )

    def _save_group_rules(self) -> None:
        with open(self._group_rules_file, "w", encoding="utf-8") as f:
            json.dump(self._group_rules, f, ensure_ascii=False, indent=4)


fortune_manager = FortuneManager()
