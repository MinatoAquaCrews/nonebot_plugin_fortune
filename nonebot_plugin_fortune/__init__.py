from nonebot import require
from nonebot import logger
from nonebot import on_command, on_regex
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import Bot, GROUP, GROUP_ADMIN, GROUP_OWNER, GroupMessageEvent, MessageSegment
from .data_source import fortune_manager
from .utils import MainThemeList
import re

__fortune_vsrsion__ = "v0.4.0"
plugin_notes = f'''
今日运势 {__fortune_vsrsion__}
[今日运势/抽签/运势] 抽签
[指定xx签] 指定特殊角色签底，需要自己尝试哦~
[设置xx签] 设置群抽签主题
[重置抽签] 重置群抽签主题
[主题列表] 查看可选的抽签主题
[抽签设置] 查看群抽签主题'''.strip()

plugin_help = on_command("今日运势帮助", permission=GROUP, priority=8, block=True)
divine = on_command("今日运势", aliases={"抽签", "运势"}, permission=GROUP, priority=8, block=True)
limit_setting = on_regex(r"指定(.*?)签", permission=GROUP, priority=8, block=True)
theme_setting = on_regex(r"设置(.*?)签", permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER, priority=8, block=True)
reset = on_command("重置抽签", permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER, priority=8, block=True)
theme_list = on_command("主题列表", permission=GROUP, priority=8, block=True)
show = on_command("抽签设置", permission=GROUP, priority=8, block=True)

'''
    超管功能
'''
refresh = on_command("刷新抽签", permission=SUPERUSER, priority=8, block=True)

scheduler = require("nonebot_plugin_apscheduler").scheduler

@plugin_help.handle()
async def show_help(bot: Bot, event: GroupMessageEvent):
    await plugin_help.finish(plugin_notes)

@show.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    theme = fortune_manager.get_setting(event)
    show_theme = MainThemeList[theme][0]
    await show.finish(f"当前群抽签主题：{show_theme}")

@theme_list.handle()
async def show_list(bot: Bot, event: GroupMessageEvent):
    msg = fortune_manager.get_main_theme_list()
    await theme_list.finish(msg)

@divine.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    image_file, status = fortune_manager.divine(spec_path=None, event=event)
    if not status:
        msg = MessageSegment.text("你今天抽过签了，再给你看一次哦🤗\n") + MessageSegment.image(image_file)
    else:
        logger.info(f"User {event.user_id} | Group {event.group_id} 占卜了今日运势")
        msg = MessageSegment.text("✨今日运势✨\n") + MessageSegment.image(image_file)
    
    await divine.finish(message=msg, at_sender=True)        

@theme_setting.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    is_theme = re.search(r"设置(.*?)签", event.get_plaintext())
    setting_theme = is_theme.group(0)[2:-1] if is_theme is not None else None

    if setting_theme is None:
        await theme_setting.finish("指定抽签主题参数错误~")
    else:
        for theme in MainThemeList.keys():
            if setting_theme in MainThemeList[theme]:
                if not fortune_manager.divination_setting(theme, event):
                    await theme_setting.finish("该抽签主题未启用~")
                else:
                    await theme_setting.finish("已设置当前群抽签主题~")
    
        await theme_setting.finish("还没有这种抽签主题哦~")

@reset.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    fortune_manager.divination_setting("random", event)
    await reset.finish("已重置当前群抽签主题为随机~")

@limit_setting.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    is_specific_type = re.search(r'指定(.*?)签', event.get_plaintext())
    limit = is_specific_type.group(0)[2:-1] if is_specific_type is not None else None

    if limit is None:
        await limit_setting.finish("指定签底参数错误~")

    if limit == "随机":
        image_file, status = fortune_manager.divine(spec_path=None, event=event)
    else:
        spec_path = fortune_manager.limit_setting_check(limit)
        if not spec_path:
            await limit_setting.finish("还不可以指定这种签哦，请确认该签底对应主题开启或图片路径存在~")
        else:
            image_file, status = fortune_manager.divine(spec_path=limit, event=event)
        
    if not status:
        msg = MessageSegment.text("你今天抽过签了，再给你看一次哦🤗\n") + MessageSegment.image(image_file)
    else:
        logger.info(f"User {event.user_id} | Group {event.group_id} 占卜了今日运势")
        msg = MessageSegment.text("✨今日运势✨\n") + MessageSegment.image(image_file)
    
    await limit_setting.finish(message=msg, at_sender=True)

@refresh.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    fortune_manager.reset_fortune()
    await limit_setting.finish("今日运势已刷新!")

# 重置每日占卜
@scheduler.scheduled_job(
    "cron",
    hour=0,
    minute=0,
)

async def _():
    fortune_manager.reset_fortune()
    logger.info("今日运势已刷新！")