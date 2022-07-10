from PIL import Image, ImageDraw, ImageFont
from typing import Optional, Tuple, Union, Dict, List
from pathlib import Path
import random
try:
    import ujson as json
except ModuleNotFoundError:
    import json

fortune_path: Path = Path(__file__).parent / "resource"

def get_copywriting() -> Tuple[str, str]:
    '''
        Read the copywriting.json, choice a luck with a random content
    '''
    _p: Path = fortune_path / "fortune" / "copywriting copy.json"
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
    _p: Path = fortune_path / "img"
    
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

def get_split_in_line(text: str, _start: int, _end: int) -> int:
    '''
        Search symbol "，"、"！" or " " in text[_start:_end]. If so, return its index, otherwise -1.
    '''
    if "，" in text[_start:_end]:
        pre_split = text.find("，", _start, _end)
    elif "！" in text[_start:_end]:
        pre_split = text.find("！", _start, _end)
    elif " " in text[_start:_end]:
        pre_split = text.find(" ", _start, _end)
    else:
        pre_split = -1

    return pre_split

def exportFilePath(originalFilePath: Path, user_id: str, group_id: str) -> Path:
    '''
        Generate the expect image path
    '''
    dirPath: Path = fortune_path / "out"
    if not dirPath.exists():
        dirPath.mkdir(exist_ok=True, parents=True)

    outPath = originalFilePath.parent.parent.parent / "out" / f"{user_id}_{group_id}.png" 
    return outPath

def sentence_modify(text: str) -> Tuple[int, List[str]]:
    length = len(text)
    temp_len = length
    result = []
    cardinality = 9 # Characters in each line
    numberOfSlices = 1
    
    if length > 4 * cardinality:
        return -1, []
    
    # Just one line    
    if length <= 9:
        result.append(text)
        return 1, result
    
    # Optimize for MORE THAN TWO columns
    space = " "
    _start = 0
    _end = len(text)
    pre_split = get_split_in_line(text, _start, _end)
    
    # 存在标点符号作为分割
    if pre_split > -1:
        '''
            如果两行摆放：第一行至多8字；标点符号后（第二行）至多8字
            一二三四五六七，空  一二三四五六七八，
            空空一二三四五六七  空一二三四五六七八
            
            如果第一行超出：第二行至多摆放 - 超出字数
            一二三四五六七八九  一二三四五六七八九
            空空，一二三四五六  空十，一二三四五六
            
            两行至多16字，尽量第二行开头空两个字
        '''
        if len(text) <= 16 and numberOfSlices == 2:
            _end = cardinality
            pre_split = get_split_in_line(text, _start, _end)
            # The first line doesn't exceed the specified number of words
            if pre_split > -1:
                fillIn = space * (8 - pre_split)
                result.append(text[:pre_split+1] + fillIn)
                
                # Calculate the rest length in Line 2 of the text
                rst_len = len(text[pre_split+1:])
                if rst_len < 8:
                    fillIn = space * 2
                    result.append(text[pre_split+1:] + fillIn)
                elif rst_len == 8:
                    fillIn = space * 1
                    
    else:               
        if length <= 18:
            '''
                一二三四五六七空空	一二三四五六七八空
                空空一二三四五六七	空空一二三四五六七
            '''
            numberOfSlices = 2
            # Even
            if length % 2 == 0:
                fillIn = space * int(9 - length / 2)
                result.append(text[:int(length / 2)] + fillIn)
                result.append(fillIn + text[int(length / 2):])
            # Odd
            else:
                fillIn = space * int(9 - (length + 1) / 2)
                result.append(text[:int((length + 1) / 2)] + fillIn)
                result.append(fillIn + space + text[int((length + 1) / 2):])
            
        elif length <= 21:
            '''
                一二三四五六七3	空	空	:int(length / 3)
                空一二三四五六	七2	空	int(length / 3):int((length - int(length / 3)) / 2) + int(length / 3)
                空空一二三四五	六	七1	int((length + int(length / 3)) / 2):
            '''
            fillIn = space * (9 - int(length / 3))
            result.append(text[:int(length / 3)] + fillIn)
            fillIn = space * (8 - int((length - int(length / 3)) / 2))
            result.append(space + text[int(length / 3):int((length + int(length / 3)) / 2)] + fillIn)
            fillIn = space * 2
            result.append(fillIn + text[int((length + int(length / 3)) / 2):])
            numberOfSlices = 3
                
        elif length <= 24:
            '''
            	一二三四五六七八1	九3	:int((length+3) / 3)
                空一二三四五六七	八2	int((length+3) / 3):int((length + int((length+3) / 3)+1) / 2)
                空空一二三四五六	七	int((length + int((length+3) / 3)+1) / 2):
            '''
            fillIn = space * (9 - int((length + 3) / 3)) # 22、23 =1; 24 =0
            result.append(text[:int((length + 3) / 3)] + fillIn)
            fillIn = space * (8 - int((length - int((length+3) / 3)+1) / 2)) # 22 =1; 23、24 =0
            result.append(space + text[9 - int((25 - length) / 2):int((length + int((length+3) / 3)+1) / 2)] + fillIn)
            result.append(space * 2 + text[int((length + int((length+3) / 3)+1) / 2):])
            numberOfSlices = 3
        
        else:
            return -1, []
        
    return numberOfSlices, result
                    
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
    _config_path: Path = fortune_path / "fortune_config.json"
    with open(_config_path, "r", encoding="utf-8") as f:
        _d: Dict[str, Union[str, bool]] = json.load(f)
    
    while True:
        picked: str = random.choice(list(_d))
        if _d.get(picked, False) is True:
            return picked.split("_flag")[0]

def drawing(_theme: Optional[str], _charac: Optional[str], user_id: str, group_id: str) -> bytes:
    '''
        Draw a specific divination
        @retval: bytes?
    '''
    # 1. Random choice a base image
    imgPath: Path = randomBasemap(_theme, _charac)
    img: Image.Image = Image.open(imgPath)
    draw = ImageDraw.Draw(img)
    
    # 2. Random choice a luck text with title
    # title, text = get_copywriting()
    title = "関係運"
    text = "只要你稍微高一些的目标为之奋斗就是好事呢"
    
    # 3. Draw
    font_size = 45
    color = "#F5F5F5"
    image_font_center: Tuple[int, int] = (140, 99)
    fontPath = {
        "title": f"{fortune_path}/font/Mamelon.otf",
        "text": f"{fortune_path}/font/sakura.ttf",
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
    numberOfSlices, result = sentence_modify(text)
    # numberOfSlices, result = 3, ["一二三四五六七  ", " 一二三四五六七八", "  一二三四五六七"]
    print(result)
    if numberOfSlices < 0:
        return 0
    
    textVertical = ""
    for i in range(0, numberOfSlices):
        font_height = len(result[i]) * (font_size + 4)
        textVertical = vertical(result[i])
        x = int(
            image_font_center[0]
            + (numberOfSlices - 2) * font_size / 2
            + (numberOfSlices - 1) * 4
            - i * (font_size + 4)
        )
        y = int(image_font_center[1] - font_height / 2)
        draw.text((x, y), textVertical, fill=color, font=ttfront)
        
    # Save
    outPath = exportFilePath(imgPath, user_id, group_id)
    img.save(outPath)
    return outPath

if __name__ == "__main__":
    img = drawing(None, None, "1234", "5678")