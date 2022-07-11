from nonebot import logger, on_command, on_regex, on_fullmatch
from nonebot.params import Depends, State, CommandArg, RegexMatched
from nonebot.typing import T_State
from nonebot.permission import SUPERUSER
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import GROUP, GROUP_ADMIN, GROUP_OWNER, Message, GroupMessageEvent, MessageSegment
from .data_source import fortune_manager
from .config import MainThemeList
from nonebot_plugin_apscheduler import scheduler

__fortune_version__ = "v0.4.4a1"
__fortune_notes__ = f'''
今日运势 {__fortune_version__}
[今日运势/抽签/运势] 抽签
[指定xx签] 指定特殊角色签底，需要自己尝试哦~
[设置xx签] 设置群抽签主题
[重置抽签] 重置群抽签主题
[主题列表] 查看可选的抽签主题
[查看主题] 查看群抽签主题'''.strip()

divine = on_command("今日运势", aliases={"抽签", "运势"}, permission=GROUP, priority=8)
limit_setting = on_regex(r"^指定(.*?)签$", permission=GROUP, priority=8, block=True)
theme_setting = on_regex(r"^设置(.*?)签$", permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER, priority=8, block=True)
reset = on_fullmatch("重置抽签", permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER, priority=8, block=True)
theme_list = on_fullmatch("主题列表", permission=GROUP, priority=8, block=True)
show = on_regex("^查看(抽签)?主题$", permission=GROUP, priority=8, block=True)

'''
    超管功能
'''
refresh = on_fullmatch("刷新抽签", permission=SUPERUSER, priority=8, block=True)

@show.handle()
async def _(event: GroupMessageEvent):
    theme = fortune_manager.get_setting(event)
    show_theme = MainThemeList[theme][0]
    await show.finish(f"当前群抽签主题：{show_theme}")

@theme_list.handle()
async def _(matcher: Matcher):
    msg = fortune_manager.get_main_theme_list()
    await matcher.finish(msg)

@divine.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    args = args.extract_plain_text()
    
    if "帮助" in args[-2:]:
        await divine.finish(__fortune_notes__)

    image_file, status = fortune_manager.divine(spec_path=None, event=event)
    if not status:
        msg = MessageSegment.text("你今天抽过签了，再给你看一次哦🤗\n") + MessageSegment.image(image_file)
    else:
        logger.info(f"User {event.user_id} | Group {event.group_id} 占卜了今日运势")
        msg = MessageSegment.text("✨今日运势✨\n") + MessageSegment.image(image_file)
    
    await divine.finish(message=msg, at_sender=True)        

async def get_user_arg(matcher: Matcher, args: str = RegexMatched(), state: T_State = State()):
    arg = args[2:-1]
    if len(arg) < 1:
        await matcher.finish("输入参数错误")
        
    return {**state, "user_arg": arg}
        
@theme_setting.handle()
async def _(event: GroupMessageEvent, state: T_State = Depends(get_user_arg)):
    user_theme = state["user_arg"]
    
    for theme in MainThemeList:
        if user_theme in MainThemeList[theme]:
            if not fortune_manager.divination_setting(theme, event):
                await theme_setting.finish("该抽签主题未启用~")
            else:
                await theme_setting.finish("已设置当前群抽签主题~")

    await theme_setting.finish("还没有这种抽签主题哦~")

@reset.handle()
async def _(event: GroupMessageEvent):
    fortune_manager.divination_setting("random", event)
    await reset.finish("已重置当前群抽签主题为随机~")

@limit_setting.handle()
async def _(event: GroupMessageEvent, state: T_State = Depends(get_user_arg)):
    limit = state["user_arg"]
    
    if limit == "随机":
        image_file, status = fortune_manager.divine(spec_path=None, event=event)
    else:
        spec_path = fortune_manager.limit_setting_check(limit)
        if not spec_path:
            await limit_setting.finish("还不可以指定这种签哦，请确认该签底对应主题开启或图片路径存在~")
        else:
            image_file, status = fortune_manager.divine(spec_path=spec_path, event=event)
        
    if not status:
        msg = MessageSegment.text("你今天抽过签了，再给你看一次哦🤗\n") + MessageSegment.image(image_file)
    else:
        logger.info(f"User {event.user_id} | Group {event.group_id} 占卜了今日运势")
        msg = MessageSegment.text("✨今日运势✨\n") + MessageSegment.image(image_file)
    
    await limit_setting.finish(message=msg, at_sender=True)

@refresh.handle()
async def _():
    fortune_manager.reset_fortune()
    await limit_setting.finish("今日运势已刷新!")

# 重置每日占卜
@scheduler.scheduled_job("cron", hour=0, minute=0, misfire_grace_time=60)
async def _():
    fortune_manager.reset_fortune()
    logger.info("今日运势已刷新！")