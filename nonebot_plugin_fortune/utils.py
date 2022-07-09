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
    if not _p.exists():
        return False

    with open(_p, "r", encoding="utf-8") as f:
        content: List[Dict[str, Union[str, int, List[str]]]]= json.load(f).get("copywriting")
        
    luck: Dict[str, Union[str, int, List[str]]] = random.choice(content)
    
    title: str = luck.get("good-luck")
    text: str = random.choice(luck.get("content"))

    return title, text

def randomBasemap(_theme: Optional[str], _charac: Optional[str]) -> Path:
    '''
        Random choose a image if no _theme indicated
        _theme and _charac are optional but need to be checked enable in function drawing
        If there is _theme but not _charac, choose from the _theme.
        If both, get the one
    '''
    _p: Path = fortune_config.fortune_path / "img"
    
    if isinstance(_theme, str):
        __p: Path = _p / _theme
        if not isinstance(_charac, str):
            images: List[str] = [str(f) for f in __p.iterdir() if f.is_file()]
            p: Path = __p / random.choice(images)
        else:
            # TODO Need check .jpg or .png and check whether _charac exists before randomBasemap
            p: Path = __p / _theme / _charac
    else:
        theme: str = random_pick_theme()
        __p: Path = _p / theme
        images: List[str] = [str(f) for f in __p.iterdir() if f.is_file()]
        p: Path = __p / random.choice(images)
        
    return p

def exportFilePath(originalFilePath: str, user_id: str, group_id: str) -> Path:
    dirPath = f"{FORTUNE_PATH}/out"
    if not os.path.exists(dirPath):
        os.makedirs(dirPath)

    outPath = Path(originalFilePath).parent.parent.parent / "out" / f"{user_id}_{group_id}.png" 
    return outPath

def decrement(text: str) -> Union[List[str], bool]:
    length = len(text)
    result = []
    cardinality = 9
    if length > 4 * cardinality:
        return False
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

def random_pick_theme() -> str:
    '''
        Random choose a theme and check whether is enable
        Return theme name
    '''
    _config_path: Path = fortune_config.fortune_path / "fortune_config.json"
    with open(_config_path, "r", encoding="utf-8") as f:
        _d: Dict[str, Union[str, bool]] = json.load(f)
    
    while True:
        picked: str = random.choice(list(_d))
        if _d.get(picked, False) is True:
            return picked.split("_flag")[0]

def drawing(theme: str, spec_path: Optional[str], user_id: str, group_id: str) -> bytes:
    '''
        Draw a specific divination
        @retval: bytes?
    '''
    fontPath = {
        "title": f"{fortune_config.fortune_path}/font/Mamelon.otf",
        "text": f"{fortune_config.fortune_path}/font/sakura.ttf",
    }
    imgPath: Path = randomBasemap(theme, spec_path)
    img: Image.Image = Image.open(imgPath)
    
    # Draw title
    draw = ImageDraw.Draw(img)
    title, text = get_copywriting()
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
    
    if isinstance(result, bool):
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