from nonebot import require
from nonebot import logger
from nonebot import on_command, on_regex
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event, GROUP, GroupMessageEvent
import os
from .data_source import FortuneManager, FORTUNE_PATH
from .utils import SpecificType, MainTheme, massage_reply
import re

fortune_manager = FortuneManager(os.path.join(FORTUNE_PATH, "fortune_data.json"))

divine = on_command("今日运势", aliases={"抽签", "运势"}, permission=GROUP, priority=8, block=True)
limit = on_regex(r"指定(.*?)签", permission=GROUP, priority=8, block=True)
setting = on_regex(r"设置(.*?)签", permission=GROUP, priority=8, block=True)
reset = on_command("重置抽签", permission=GROUP, priority=8, block=True)
show = on_command("抽签设置", permission=GROUP, priority=8, block=True)

scheduler = require("nonebot_plugin_apscheduler").scheduler

@show.handle()
async def show_theme(bot: Bot, event: GroupMessageEvent, state: T_State):
    '''
        显示当前抽签主题
    '''
    if fortune_manager.main_theme == MainTheme.PCR:
        theme = "PCR"
    elif fortune_manager.main_theme == MainTheme.GENSHIN:
        theme = "Genshin Impact"
    elif fortune_manager.main_theme == MainTheme.VTUBER:
        theme = "Vtuber"
    elif fortune_manager.main_theme == MainTheme.TOUHOU:
        theme = "东方"
    elif fortune_manager.main_theme == MainTheme.RANDOM:
        theme = "随机"

    msg = f"当前抽签主题：{theme}"
    await bot.send(event=event, message=msg, at_sender=False)

@divine.handle()
async def divine(bot: Bot, event: GroupMessageEvent, state: T_State):
    image_file, status = fortune_manager.divine(SpecificType.RANDOM, event)
    if status:
        logger.info(f"User {event.user_id} | Group {event.group_id} 占卜了今日运势")
        msg = massage_reply(image_file, "✨今日运势✨\n")
        await bot.send(event=event, message=msg, at_sender=True)
    else:
        msg = massage_reply(image_file, "你今天抽过签了，再给你看一次哦🤗\n")
        await bot.send(event=event, message=msg, at_sender=True)

@setting.handle()
async def theme_setting(bot: Bot, event: GroupMessageEvent, state: T_State):
    '''
        设置抽签主题
    '''
    is_theme = re.search(r"设置(.*?)签", event.get_plaintext())
    theme = is_theme.group(0)[2:-1] if is_theme is not None else None
    # logger.info(theme)
    if theme is None:
        await theme.finish("给个设置OK?")
    elif theme == "PCR" or theme == "公主链接":
        fortune_manager.main_theme = MainTheme.PCR
    elif theme == "原神" or theme == "genshin" or theme == "Genshin":
        fortune_manager.main_theme = MainTheme.GENSHIN
    elif theme == "vtb" or theme == "vtuber" or theme == "Vtuber" or theme == "Vtb":
        fortune_manager.main_theme = MainTheme.VTUBER
    elif theme == "东方":
        fortune_manager.main_theme = MainTheme.TOUHOU
    else:
        await setting.finish("好像还没这种签哦~")

    await bot.send(event=event, message="已设置抽签主题~", at_sender=False)

@reset.handle()
async def _(bot: Bot, event: GroupMessageEvent, state: T_State):
    '''
        重置抽签主题
    '''
    fortune_manager.main_theme = MainTheme.RANDOM
    fortune_manager.specific_limit = SpecificType.RANDOM
    await bot.send(event=event, message="已重置抽签主题为随机~", at_sender=False)

@limit.handle()
async def limit_setting(bot: Bot, event: GroupMessageEvent, state: T_State):
    '''
        单独指定某种抽签签底
    '''
    is_specific_type = re.search(r'指定(.*?)签', event.get_plaintext())
    s_limit = is_specific_type.group(0)[2:-1] if is_specific_type is not None else None
    # logger.info(limit)
    if s_limit is None:
        await limit.finish("还不可以指定这种签哦~")
    
    if s_limit == "凯露" or s_limit == "臭鼬":
        specific_limit = SpecificType.KAILU
    elif s_limit == "可可萝" or s_limit == "妈":
        specific_limit = SpecificType.KEKELUO
    elif s_limit == "可莉" or s_limit == "哒哒哒":
        specific_limit = SpecificType.KLEE
    elif s_limit == "刻晴" or s_limit == "刻师傅":
        specific_limit = SpecificType.KEQING
    elif s_limit == "芭芭拉":
        specific_limit = SpecificType.BABALA
    elif s_limit == "白上吹雪" or s_limit == "FBK" or s_limit == "fbk" or s_limit == "小狐狸":
        specific_limit = SpecificType.FUBUKI
    elif s_limit == "阿夸" or s_limit == "夸" or s_limit == "Aqua" or s_limit == "aqua":
        specific_limit = SpecificType.AQUA
    elif s_limit == "灵梦":
        specific_limit = SpecificType.REIMU
    elif s_limit == "魔理沙":
        specific_limit = SpecificType.MARISA
    else:
        specific_limit = SpecificType.RANDOM
    
    image_file, status = fortune_manager.divine(specific_limit, event)
    if status:
        logger.info(f"User {event.user_id} | Group {event.group_id} 占卜了今日运势")
        if specific_limit == SpecificType.RANDOM:
            await bot.send(event=event, message="未定义的指定抽签，已指定随机", at_sender=True)
        
        msg = massage_reply(image_file, "✨今日运势✨\n")
        await bot.send(event=event, message=msg, at_sender=True)
    else:
        msg = massage_reply(image_file, "你今天抽过签了，再给你看一次哦🤗\n")
        await bot.send(event=event, message=msg, at_sender=True)


# 重置每日占卜
@scheduler.scheduled_job(
    "cron",
    hour=0,
    minute=0,
)

async def _():
    fortune_manager.reset_fortune()
    logger.info("今日运势已刷新！")