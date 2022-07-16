from PIL import Image, ImageDraw, ImageFont
from typing import Optional, Tuple, Union, Dict, List
from pathlib import Path
import random
try:
    import ujson as json
except ModuleNotFoundError:
    import json

from .config import fortune_config

'''
    抽签主题开关，当随机抽签时判断某主题是否开启
'''
MainThemeEnable: Dict[str, bool] = {
    "pcr": fortune_config.pcr_flag,
    "genshin": fortune_config.genshin_flag,
    "hololive": fortune_config.hololive_flag,
    "touhou": fortune_config.touhou_flag,
    "touhou_lostword": fortune_config.touhou_lostword_flag,
    "touhou_old": fortune_config.touhou_olg_flag,
    "onmyoji": fortune_config.onmyoji_flag,
    "azure": fortune_config.azure_flag,
    "asoul": fortune_config.asoul_flag,
    "arknights": fortune_config.arknights_flag,
    "granblue_fantasy": fortune_config.granblue_fantasy_flag,
    "punishing": fortune_config.punishing_flag,
    "pretty_derby": fortune_config.pretty_derby_flag,
    "dc4": fortune_config.dc4_flag,
    "einstein": fortune_config.einstein_flag,
    "sweet_illusion": fortune_config.sweet_illusion_flag,
    "liqingge": fortune_config.liqingge_flag,
    "hoshizora": fortune_config.hoshizora_flag,
    "sakura": fortune_config.sakura_flag,
    "summer_pockets": fortune_config.summer_pockets_flag,
    "amazing_grace": fortune_config.amazing_grace_flag
}

def get_copywriting() -> Tuple[str, str]:
    '''
        Read the copywriting.json, choice a luck with a random content
    '''
    _p: Path = fortune_config.fortune_path / "fortune" / "copywriting.json"
    content: List[Dict[str, Union[str, int, List[str]]]] = {}

    with open(_p, "r", encoding="utf-8") as f:
        content = json.load(f).get("copywriting")
        
    luck: Dict[str, Union[str, int, List[str]]] = random.choice(content)
    
    title: str = luck.get("good-luck")
    text: str = random.choice(luck.get("content"))

    return title, text

def randomBasemap(_theme: str, _spec_path: Optional[str]) -> str:
    try_time = 0
    if isinstance(_spec_path, str):
        _p: Path = fortune_config.fortune_path / "img"
        p: Path =_p / _spec_path
        return p
    else:
        if _theme == "random":
            __p: Path = fortune_config.fortune_path / "img"
            # Each dir is a theme
            themes: List[str] = [str(f) for f in __p.iterdir() if f.is_dir()]
            while True:
                picked = random.choice(themes)
                picked_theme = picked + "_flag"
                if MainThemeEnable.get(picked_theme) is True:
                    break
                else:
                    try_time += 1

                if try_time == len(list(MainThemeEnable)):
                    break

            _p: Path = __p / picked
            # Each file is a image
            images: List[str] = [str(f) for f in _p.iterdir() if f.is_file()]
            p: Path = _p / random.choice(images)
        else:
            _p: Path = fortune_config.fortune_path / "img" / _theme
            images: List[str] = [str(f) for f in _p.iterdir() if f.is_file()]
            p: Path = _p / random.choice(images)
        
        return p

def drawing(_theme: str, _spec_path: Optional[str], gid: str, uid: str) -> Path:
    # 1. Random choice a base image
    imgPath = randomBasemap(_theme, _spec_path)
    img: Image.Image = Image.open(imgPath)
    draw = ImageDraw.Draw(img)
    
    # 2. Random choice a luck text with title
    title, text = get_copywriting()
    
    # 3. Draw
    font_size = 45
    color = "#F5F5F5"
    image_font_center = (140, 99)
    fontPath = {
        "title": f"{fortune_config.fortune_path}/font/Mamelon.otf",
        "text": f"{fortune_config.fortune_path}/font/sakura.ttf",
    }
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
    outPath = exportFilePath(imgPath, gid, uid)
    img.save(outPath)
    return outPath

def exportFilePath(originalFilePath: Path, gid: str, uid: str) -> Path:
    dirPath: Path = fortune_config.fortune_path / "out"
    if not dirPath.exists():
        dirPath.mkdir(exist_ok=True, parents=True)

    outPath: Path = originalFilePath.parent.parent.parent / "out" / f"{uid}_{gid}.png" 
    return outPath

def decrement(text: str) -> List[str]:
    length = len(text)
    result = []
    cardinality = 9
    if length > 4 * cardinality:
        raise Exception
    
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

def vertical(_str: List[str]) -> str:
    _list = []
    for s in _str:
        _list.append(s)
    return "\n".join(_list)