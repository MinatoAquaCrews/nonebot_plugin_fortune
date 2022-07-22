from PIL import Image, ImageDraw, ImageFont
from typing import Optional, Tuple, Union, Dict, List
from pathlib import Path
import random
try:
    import ujson as json
except ModuleNotFoundError:
    import json

from .config import fortune_config

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

def randomBasemap(_theme: str, _spec_path: Optional[str]) -> Path:
    if isinstance(_spec_path, str):
        p: Path = fortune_config.fortune_path / "img" / _spec_path
        return p

    if _theme == "random":
        __p: Path = fortune_config.fortune_path / "img"
        # Each dir is a theme, remember add _flag after the names of themes
        themes: List[str] = [f.name for f in __p.iterdir() if f.is_dir() and theme_flag_check(f.name + "_flag")]
        picked = random.choice(themes)

        _p: Path = __p / picked
        # Each file is a posix path of images
        images: List[Path] = [i for i in _p.iterdir() if i.is_file()]
        p: Path = random.choice(images)
    else:
        _p: Path = fortune_config.fortune_path / "img" / _theme
        images: List[Path] = [i for i in _p.iterdir() if i.is_file()]
        p: Path = random.choice(images)
    
    return p

def drawing(_theme: str, _spec_path: Optional[str], gid: str, uid: str) -> Path:
    # 1. Random choice a base image
    imgPath: Path = randomBasemap(_theme, _spec_path)
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

    outPath: Path = originalFilePath.parent.parent.parent / "out" / f"{gid}_{uid}.png" 
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

def theme_flag_check(_theme: str) -> bool:
    '''
        Read the config json, return the status of a theme
    '''
    flag_config_path: Path = fortune_config.fortune_path / "fortune_config.json"
    with flag_config_path.open("r", encoding="utf-8") as f:
        data: Dict[str, bool] = json.load(f)
    
    return data.get(_theme, False)

__all__ = [
    drawing, theme_flag_check
]