import json
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Union

from nonebot import get_driver
from nonebot.log import logger
from pydantic import BaseModel, Extra, root_validator

from .download import ResourceError, download_resource

"""
	抽签主题对应表，第一键值为“抽签设置”或“主题列表”展示的主题名称
	Key-Value: 主题资源文件夹名-主题别名
"""
FortuneThemesDict: Dict[str, List[str]] = {
    "random": ["随机"],
    "amazing_grace": ["奇异恩典"],
    "arknights": ["明日方舟", "方舟", "arknights", "鹰角", "Arknights", "舟游"],
    "asoul": ["Asoul", "asoul", "a手", "A手", "as", "As"],
    "azure": ["碧蓝航线", "碧蓝", "azure", "Azure"],
    "dc4": ["dc4", "DC4", "Dc4"],
    "einstein": ["爱因斯坦携爱敬上", "爱因斯坦", "einstein", "Einstein"],
    "genshin": ["原神", "Genshin Impact", "genshin", "Genshin", "op", "原批"],
    "granblue_fantasy": ["碧蓝幻想", "Granblue Fantasy", "granblue fantasy", "幻想"],
    "hololive": ["Hololive", "hololive", "Vtb", "vtb", "管人", "Holo", "holo", "管人痴"],
    "hoshizora": ["星空列车与白的旅行", "星空列车"],
    "liqingge": ["李清歌", "清歌"],
    "onmyoji": ["阴阳师", "yys", "Yys", "痒痒鼠"],
    "pcr": ["PCR", "公主链接", "公主连结", "Pcr", "pcr"],
    "pretty_derby": ["赛马娘", "马", "马娘", "赛马"],
    "punishing": ["战双", "战双帕弥什"],
    "sakura": ["樱色之云绯色之恋", "樱云之恋", "樱云绯恋", "樱云"],
    "summer_pockets": ["夏日口袋", "夏兜", "sp", "SP"],
    "sweet_illusion": ["灵感满溢的甜蜜创想", "甜蜜一家人", "富婆妹"],
    "touhou": ["东方", "touhou", "Touhou", "车万"],
    "touhou_lostword": ["东方归言录", "东方lostword", "touhou lostword"],
    "touhou_old": ["旧东方", "旧版东方", "老东方", "老版东方", "经典东方"],
    "warship_girls_r": ["战舰少女R", "舰r", "舰R", "wsgr", "WSGR", "战舰少女r"],
}


class PluginConfig(BaseModel, extra=Extra.ignore):
    fortune_path: Path = Path(__file__).parent / "resource"


class ThemesFlagConfig(BaseModel, extra=Extra.ignore):
    """
    Switches of themes only valid in random divination.
    Make sure NOT ALL FALSE!
    """

    amazing_grace_flag: bool = True
    arknights_flag: bool = True
    asoul_flag: bool = True
    azure_flag: bool = True
    dc4_flag: bool = True
    einstein_flag: bool = True
    genshin_flag: bool = True
    granblue_fantasy_flag: bool = True
    hololive_flag: bool = True
    hoshizora_flag: bool = True
    liqingge_flag: bool = True
    onmyoji_flag: bool = True
    pcr_flag: bool = True
    pretty_derby_flag: bool = True
    punishing_flag: bool = True
    sakura_flag: bool = True
    summer_pockets_flag: bool = True
    sweet_illusion_flag: bool = True
    touhou_flag: bool = True
    touhou_lostword_flag: bool = True
    touhou_old_flag: bool = True
    warship_girls_r_flag: bool = True

    @root_validator
    def check_all_disabled(cls, values) -> None:
        """Check whether all themes are DISABLED"""
        flag: bool = False
        for theme in values:
            if values.get(theme, False):
                flag = True
                break

        if not flag:
            raise ValueError("Fortune themes ALL disabled! Please check!")

        return values


class FortuneConfig(PluginConfig, ThemesFlagConfig):
    pass


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj) -> Union[str, Any]:
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(obj, date):
            return obj.strftime("%Y-%m-%d")

        return json.JSONEncoder.default(self, obj)


driver = get_driver()
fortune_config: PluginConfig = PluginConfig.parse_obj(driver.config.dict())
themes_flag_config: ThemesFlagConfig = ThemesFlagConfig.parse_obj(driver.config.dict())


@driver.on_startup
async def fortune_check() -> None:
    if not fortune_config.fortune_path.exists():
        fortune_config.fortune_path.mkdir(parents=True, exist_ok=True)

    """Check fonts"""
    fonts_path: Path = fortune_config.fortune_path / "font"
    if not fonts_path.exists():
        fonts_path.mkdir(parents=True, exist_ok=True)

    if not (fonts_path / "Mamelon.otf").exists():
        raise ResourceError("Resource Mamelon.otf is missing! Please check!")

    if not (fonts_path / "sakura.ttf").exists():
        raise ResourceError("Resource sakura.ttf is missing! Please check!")

    """
		Try to get the latest copywriting from the repository.
	"""
    copywriting_path: Path = (
        fortune_config.fortune_path / "fortune" / "copywriting.json"
    )
    if not copywriting_path.parent.exists():
        copywriting_path.parent.mkdir(parents=True, exist_ok=True)

    ret = await download_resource(copywriting_path, "copywriting.json", "fortune")
    if not ret and not copywriting_path.exists():
        raise ResourceError("Resource copywriting.json is missing! Please check!")

    """
		Check rules and data files
	"""
    fortune_data_path: Path = fortune_config.fortune_path / "fortune_data.json"
    fortune_setting_path: Path = fortune_config.fortune_path / "fortune_setting.json"
    group_rules_path: Path = fortune_config.fortune_path / "group_rules.json"
    specific_rules_path: Path = fortune_config.fortune_path / "specific_rules.json"

    if not fortune_data_path.exists():
        logger.warning("Resource fortune_data.json is missing, initialized one...")

        with fortune_data_path.open("w", encoding="utf-8") as f:
            json.dump(dict(), f, ensure_ascii=False, indent=4)
    else:
        """
        In version 0.4.10, the format of fortune_data.json is changed from v0.4.9 and older.
        1. Remove useless keys "gid", "uid" and "nickname"
        2. Transfer the key "is_divined" to "last_sign_date"
        """
        with open(fortune_data_path, "r", encoding="utf-8") as f:
            _data: Dict[
                str, Dict[str, Dict[str, Union[str, bool, int, date]]]
            ] = json.load(f)

        for gid in _data:
            if _data[gid]:
                for uid in _data[gid]:
                    """
                    From this time, if is_divined is False, don't care the last sign-in date.
                    Otherwise, the last sign-in date is TODAY.
                    """
                    try:
                        _data[gid][uid].pop("nickname")
                    except KeyError:
                        pass

                    try:
                        _data[gid][uid].pop("gid")
                    except KeyError:
                        pass

                    try:
                        _data[gid][uid].pop("uid")
                    except KeyError:
                        pass

                    try:
                        is_divined: bool = _data[gid][uid].pop(
                            "is_divined"
                        )  # type: ignore
                        if is_divined:
                            _data[gid][uid].update({"last_sign_date": date.today()})
                        else:
                            _data[gid][uid].update({"last_sign_date": 0})
                    except KeyError:
                        pass

        with open(fortune_data_path, "w", encoding="utf-8") as f:
            json.dump(_data, f, ensure_ascii=False, indent=4, cls=DateTimeEncoder)

    _flag: bool = False
    if not group_rules_path.exists():
        # In version 0.4.x, compatible job will be done automatically if group_rules.json doesn't exist
        if fortune_setting_path.exists():
            # Try to transfer from the old setting json
            ret = group_rules_transfer(fortune_setting_path, group_rules_path)
            if ret:
                logger.info("旧版 fortune_setting.json 文件中群聊抽签主题设置已更新至 group_rules.json")
                _flag = True

        if not _flag:
            # If failed or fortune_setting_path doesn't exist, initialize group_rules.json instead
            with group_rules_path.open("w", encoding="utf-8") as f:
                json.dump(dict(), f, ensure_ascii=False, indent=4)

            logger.info("旧版 fortune_setting.json 文件中群聊抽签主题设置不存在，初始化 group_rules.json")

    _flag = False
    if not specific_rules_path.exists():
        # In version 0.4.9 and 0.4.10, data transfering will be done automatically if specific_rules.json doesn't exist
        if fortune_setting_path.exists():
            # Try to transfer from the old setting json
            ret = specific_rules_transfer(fortune_setting_path, specific_rules_path)
            if ret:
                # Delete the old fortune_setting json if the transfer is OK
                fortune_setting_path.unlink()

                logger.info("旧版 fortune_setting.json 文件中签底指定规则已更新至 specific_rules.json")
                logger.warning("指定签底抽签功能将在 v0.5.0 弃用")
                _flag = True

        if not _flag:
            # Try to download it from repo
            ret = await download_resource(specific_rules_path, "specific_rules.json")
            if ret:
                logger.info(f"Downloaded specific_rules.json from repo")
            else:
                # If failed, initialize specific_rules.json instead
                with specific_rules_path.open("w", encoding="utf-8") as f:
                    json.dump(dict(), f, ensure_ascii=False, indent=4)

                logger.info(
                    "旧版 fortune_setting.json 文件中签底指定规则不存在，初始化 specific_rules.json"
                )
                logger.warning("指定签底抽签功能将在 v0.5.0 弃用")


def group_rules_transfer(fortune_setting_dir: Path, group_rules_dir: Path) -> bool:
    """
    Transfer the group_rule in fortune_setting.json to group_rules.json
    """
    with open(fortune_setting_dir, "r", encoding="utf-8") as f:
        _setting: Dict[str, Dict[str, Union[str, List[str]]]] = json.load(f)

    group_rules = _setting.get("group_rule", None)  # Old key is group_rule

    with open(group_rules_dir, "w", encoding="utf-8") as f:
        if group_rules is None:
            json.dump(dict(), f, ensure_ascii=False, indent=4)
            return False
        else:
            json.dump(group_rules, f, ensure_ascii=False, indent=4)
            return True


def specific_rules_transfer(
    fortune_setting_dir: Path, specific_rules_dir: Path
) -> bool:
    """
    Transfer the specific_rule in fortune_setting.json to specific_rules.json
    """
    with open(fortune_setting_dir, "r", encoding="utf-8") as f:
        _setting: Dict[str, Dict[str, Union[str, List[str]]]] = json.load(f)

    specific_rules = _setting.get("specific_rule", None)  # Old key is specific_rule

    with open(specific_rules_dir, "w", encoding="utf-8") as f:
        if not specific_rules:
            json.dump(dict(), f, ensure_ascii=False, indent=4)
            return False
        else:
            json.dump(specific_rules, f, ensure_ascii=False, indent=4)
            return True
