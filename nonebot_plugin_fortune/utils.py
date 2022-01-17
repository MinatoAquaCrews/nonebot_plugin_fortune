import os
import random
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from enum import Enum

try:
    import ujson as json
except ModuleNotFoundError:
    import json

from .data_source import FORTUNE_PATH

class MainTheme(Enum):

    RANDOM  = "_random"
    PCR     = "_pcr"
    GENSHIN = "_genshin"
    VTUBER  = "_vtuber"
    TOUHOU  = "_touhou" 

class SpecificType(Enum):

    RANDOM = "_random"
    KAILU   = "_kailu"
    KEKELUO = "_kekeluo"
    KLEE    = "_klee"
    KEQING  = "_keqing"
    BABALA  = "_babala"
    FUBUKI  = "_fubuki"
    AQUA    = "_aqua"
    REIMU   = "_reimu"
    MARISA  = "_marisa"

def copywriting():
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

def randomBasemap(theme, limit):
    if theme == MainTheme.RANDOM:
        if limit == SpecificType.AQUA:
            p = f"{FORTUNE_PATH}/img/vtuber"
            return p + "/" + "frame_18.png"
        elif limit == SpecificType.BABALA:
            p = f"{FORTUNE_PATH}/img/genshin"
            return p + "/" + "frame_2.png"
        elif limit == SpecificType.FUBUKI:
            p = f"{FORTUNE_PATH}/img/vtuber"
            return p + "/" + "frame_17.png"
        elif limit == SpecificType.KAILU:
            p = f"{FORTUNE_PATH}/img/pcr"
            return p + "/" + random.choice(["frame_1.png", "frame_2.png"])
        elif limit == SpecificType.KEKELUO:
            p = f"{FORTUNE_PATH}/img/pcr"
            return p + "/" + random.choice(["frame_41.png", "frame_42.png"])
        elif limit == SpecificType.KEQING:
            p = f"{FORTUNE_PATH}/img/genshin"
            return p + "/" + "frame_23.png"
        elif limit == SpecificType.KLEE:
            p = f"{FORTUNE_PATH}/img/genshin"
            return p + "/" + "frame_24.png"
        elif limit == SpecificType.REIMU:
            p = f"{FORTUNE_PATH}/img/touhou"
            return p + "/" + "frame_1.png"
        elif limit == SpecificType.MARISA:
            p = f"{FORTUNE_PATH}/img/touhou"
            return p + "/" + "frame_2.png"
        else:
            _p = f"{FORTUNE_PATH}/img"
            p = _p + "/" + random.choice(os.listdir(_p))
            return p + "/" + random.choice(os.listdir(p))

    elif theme == MainTheme.PCR:
        p = f"{FORTUNE_PATH}/img/pcr"
        return p + "/" + random.choice(os.listdir(p))
    elif theme == MainTheme.GENSHIN:
        p = f"{FORTUNE_PATH}/img/genshin"
        return p + "/" + random.choice(os.listdir(p))
    elif theme == MainTheme.VTUBER:
        p = f"{FORTUNE_PATH}/img/vtuber"
        return p + "/" + random.choice(os.listdir(p))
    elif theme == MainTheme.TOUHOU:
        p = f"{FORTUNE_PATH}/img/touhou"
        return p + "/" + random.choice(os.listdir(p))
    else:
        raise Exception("Specific theme is undefined")

def drawing(theme, limit, user_id: int, group_id: int):
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

def exportFilePath(originalFilePath, user_id: int, group_id: int):
    outPath = str(Path(originalFilePath).parent.parent).replace("/img", "/out/") + f"{str(user_id)}_{str(group_id)}.png"
    dirPath = f"{FORTUNE_PATH}/out"
    if not os.path.exists(dirPath):
        os.makedirs(dirPath)

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

def massage_reply(image_file, text):
    msg = [
        {
            "type": "text",
            "data": {
                "text": text
            }
        }, 
        {
            "type": "image",
            "data": {
                "file": f"file:{Path(image_file).absolute()}",
            }
        }
    ]

    return msg