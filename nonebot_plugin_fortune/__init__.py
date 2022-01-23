from nonebot import require
from nonebot import logger
from nonebot import on_command, on_regex
from nonebot.typing import T_State
from nonebot.permission import SUPERUSER
from nonebot.adapters.cqhttp import Bot, GROUP, GROUP_ADMIN, GROUP_OWNER, GroupMessageEvent, MessageSegment
from .data_source import fortune_manager
from .utils import MainThemeList, SpecificTypeList
import re

divine = on_command("今日运势", aliases={"抽签", "运势"}, permission=GROUP, priority=8, block=True)
limit_setting = on_regex(r"指定(.*?)签", permission=GROUP, priority=8, block=True)
theme_setting = on_regex(r"设置(.*?)签", permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER, priority=8, block=True)
reset = on_command("重置抽签", permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER, priority=8, block=True)
show = on_command("抽签设置", permission=GROUP, priority=8, block=True)

scheduler = require("nonebot_plugin_apscheduler").scheduler

@show.handle()
async def _(bot: Bot, event: GroupMessageEvent, state: T_State):
    theme = fortune_manager.get_setting(event)
    show_theme = MainThemeList[theme][0]
    await show.finish(message=f"当前群抽签主题：{show_theme}")

@divine.handle()
async def _(bot: Bot, event: GroupMessageEvent, state: T_State):
    image_file, status = fortune_manager.divine(limit=None, event=event)
    if not status:
        msg = MessageSegment.text("你今天抽过签了，再给你看一次哦🤗\n") + MessageSegment.image(image_file)
    else:
        logger.info(f"User {event.user_id} | Group {event.group_id} 占卜了今日运势")
        msg = MessageSegment.text("✨今日运势✨\n") + MessageSegment.image(image_file)
    
    await divine.finish(message=msg, at_sender=True)        

@theme_setting.handle()
async def _(bot: Bot, event: GroupMessageEvent, state: T_State):
    is_theme = re.search(r"设置(.*?)签", event.get_plaintext())
    setting_theme = is_theme.group(0)[2:-1] if is_theme is not None else None

    if setting_theme is None:
        await theme_setting.finish(message="指定抽签主题参数错误~")
    else:
        for theme in MainThemeList.keys():
            if setting_theme in MainThemeList[theme]:
                fortune_manager.divination_setting(theme, event) 
                await theme_setting.finish(message="已设置当前群抽签主题~")
    
        await theme_setting.finish(message="还没有这种抽签主题哦~")

@reset.handle()
async def _(bot: Bot, event: GroupMessageEvent, state: T_State):
    fortune_manager.divination_setting("random", event)
    await reset.finish(message="已重置当前群抽签主题为随机~")

@limit_setting.handle()
async def _(bot: Bot, event: GroupMessageEvent, state: T_State):
    is_specific_type = re.search(r'指定(.*?)签', event.get_plaintext())
    limit = is_specific_type.group(0)[2:-1] if is_specific_type is not None else None

    if limit is None:
        await limit_setting.finish("指定签底参数错误~")

    if not SpecificTypeList.get(limit):
        await limit_setting.finish("还不可以指定这种签哦~")
    else:
        if limit == "随机":
            image_file, status = fortune_manager.divine(limit=None, event=event)
        else:
            image_file, status = fortune_manager.divine(limit=limit, event=event)
        
    if not status:
        msg = MessageSegment.text("你今天抽过签了，再给你看一次哦🤗\n") + MessageSegment.image(image_file)
    else:
        logger.info(f"User {event.user_id} | Group {event.group_id} 占卜了今日运势")
        msg = MessageSegment.text("✨今日运势✨\n") + MessageSegment.image(image_file)
    
    await limit_setting.finish(message=msg, at_sender=True)          


# 重置每日占卜
@scheduler.scheduled_job(
    "cron",
    hour=0,
    minute=0,
)

async def _():
    fortune_manager.reset_fortune()
    logger.info("今日运势已刷新！")