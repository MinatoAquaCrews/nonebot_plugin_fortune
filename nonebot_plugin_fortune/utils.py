import os
import random
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from typing import Optional

try:
    import ujson as json
except ModuleNotFoundError:
    import json

from .data_source import FORTUNE_PATH

'''
    抽签主题对应表，第一键值为“抽签设置”展示的主题名称
    Key-Value: 主题资源文件夹名-设置主题别名
'''
MainThemeList = {
    "random":   ["随机"],
    "pcr":      ["PCR", "公主链接", "公主连接", "Pcr", "pcr"],
    "genshin":  ["Genshin Impact", "原神", "genshin", "Genshin"],
    "vtuber":   ["Vtuber", "VTB", "Vtb", "vtb", "管人"],
    "touhou":   ["东方", "touhou", "Touhou"]
}

'''
    指定特定签底对应表，应指定对应图片路径（./resource/img后）；random仅为标识
    Key-Value: 签底别名-图片路径 
'''
SpecificTypeList = {
    "随机":     ["random"],
    "凯露":     ["pcr/frame_1.jpg", "pcr/frame_2.jpg"],
    "臭鼬":     ["pcr/frame_1.jpg", "pcr/frame_2.jpg"],
    "可可萝":   ["pcr/frame_41.jpg", "pcr/frame_42.jpg"],
    "可莉":     ["genshin/frame_24.jpg"],
    "刻晴":     ["genshin/frame_23.jpg"],
    "芭芭拉":   ["genshin/frame_2.jpg"],
    "行秋":     ["genshin/frame_5.jpg"],
    "fbk":     ["vtuber/frame_17.png"],
    "白上吹雪": ["vtuber/frame_17.png"],
    "阿夸":     ["vtuber/frame_18.png"],
    "debu":     ["vtuber/frame_18.png"],
    "tskk":     ["vtuber/frame_7.png"],
    "桐生可可": ["vtuber/frame_7.png"],
    "蛆皇":     ["vtuber/frame_7.png"],
    "灵梦":     ["touhou/frame_1.jpg"],
    "魔理沙":   ["touhou/frame_2.jpg"],
    "妖梦":     ["touhou/frame_3.png"],
    "芙兰朵露": ["touhou/frame_4.png"],
    "二小姐":   ["touhou/frame_4.png"],
    "大小姐":   ["touhou/frame_5.png"],
    "幽幽子":   ["touhou/frame_6.jpg"],
    "八云紫":   ["touhou/frame_7.jpg"],
    "妹红":     ["touhou/frame_15.jpg"],
    "咲夜":     ["touhou/frame_16.png"],
}

def copywriting() -> str:
    p = f"{FORTUNE_PATH}/fortune/copywriting.json"
    if not os.path.exists(p):
        return False

    with open(p, "r", encoding="utf-8") as f:
        content = json.loads(f.read())

    return random.choice(content["copywriting"])

def getTitle(structure):
    p = f"{FORTUNE_PATH}/fortune/goodLuck.json"
    if not os.path.exists(p):
        return False

    with open(p, "r", encoding="utf-8") as f:
        content = json.loads(f.read())

    for i in content["types_of"]:
        if i["good-luck"] == structure["good-luck"]:
            return i["name"]
    raise Exception("Configuration file error")

def randomBasemap(theme: str, limit: Optional[str]) -> str:
    if limit:
        _p = f"{FORTUNE_PATH}/img"
        specific_path = random.choice(SpecificTypeList[limit])     
        p = os.path.join(_p, specific_path)
        
        return p
    else:
        if theme == "random":
            __p = f"{FORTUNE_PATH}/img"
            _p = os.path.join(__p, random.choice(os.listdir(__p)))
            p = os.path.join(_p, random.choice(os.listdir(_p)))
        else:
            _p = os.path.join(f"{FORTUNE_PATH}/img", theme)
            p = os.path.join(_p, random.choice(os.listdir(_p)))
        
        return p

def drawing(theme: str, limit: Optional[str], user_id: int, group_id: int) -> Path:
    fontPath = {
        "title": f"{FORTUNE_PATH}/font/Mamelon.otf",
        "text": f"{FORTUNE_PATH}/font/sakura.ttf",
    }
    imgPath = randomBasemap(theme, limit)
    img = Image.open(imgPath)
    # Draw title
    draw = ImageDraw.Draw(img)
    text = copywriting()
    title = getTitle(text)
    text = text["content"]
    font_size = 45
    color = "#F5F5F5"
    image_font_center = (140, 99)
    ttfront = ImageFont.truetype(fontPath["title"], font_size)
    font_length = ttfront.getsize(title)
    draw.text(
        (
            image_font_center[0] - font_length[0] / 2,
            image_font_center[1] - font_length[1] / 2,
        ),
        title,
        fill=color,
        font=ttfront,
    )
    # Text rendering
    font_size = 25
    color = "#323232"
    image_font_center = [140, 297]
    ttfront = ImageFont.truetype(fontPath["text"], font_size)
    result = decrement(text)
    if not result[0]:
        return
    textVertical = []
    for i in range(0, result[0]):
        font_height = len(result[i + 1]) * (font_size + 4)
        textVertical = vertical(result[i + 1])
        x = int(
            image_font_center[0]
            + (result[0] - 2) * font_size / 2
            + (result[0] - 1) * 4
            - i * (font_size + 4)
        )
        y = int(image_font_center[1] - font_height / 2)
        draw.text((x, y), textVertical, fill=color, font=ttfront)
    # Save
    outPath = exportFilePath(imgPath, user_id, group_id)
    img.save(outPath)
    return outPath

def exportFilePath(originalFilePath: str, user_id: int, group_id: int) -> Path:
    dirPath = f"{FORTUNE_PATH}/out"
    if not os.path.exists(dirPath):
        os.makedirs(dirPath)

    outPath = Path(originalFilePath).parent.parent.parent / "out" / f"{str(user_id)}_{str(group_id)}.png" 
    return outPath

def decrement(text):
    length = len(text)
    result = []
    cardinality = 9
    if length > 4 * cardinality:
        return [False]
    numberOfSlices = 1
    while length > cardinality:
        numberOfSlices += 1
        length -= cardinality
    result.append(numberOfSlices)
    # Optimize for two columns
    space = " "
    length = len(text)
    if numberOfSlices == 2:
        if length % 2 == 0:
            # even
            fillIn = space * int(9 - length / 2)
            return [
                numberOfSlices,
                text[: int(length / 2)] + fillIn,
                fillIn + text[int(length / 2) :],
            ]
        else:
            # odd number
            fillIn = space * int(9 - (length + 1) / 2)
            return [
                numberOfSlices,
                text[: int((length + 1) / 2)] + fillIn,
                fillIn + space + text[int((length + 1) / 2) :],
            ]
    for i in range(0, numberOfSlices):
        if i == numberOfSlices - 1 or numberOfSlices == 1:
            result.append(text[i * cardinality :])
        else:
            result.append(text[i * cardinality : (i + 1) * cardinality])
    return result


def vertical(str):
    list = []
    for s in str:
        list.append(s)
    return "\n".join(list)
