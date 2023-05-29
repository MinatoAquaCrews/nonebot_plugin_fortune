import json
import random
import os
from pathlib import Path
from typing import List, Optional, Tuple

from PIL import Image, ImageDraw, ImageFont

from .config import fortune_config, themes_flag_config


def get_copywriting(filename: str) -> Tuple[str, str]:
    '''
            Read the copywriting.json, choice a luck with a random content
    '''
    _p: Path = fortune_config.fortune_path / "fortune" / "copywriting.json"
    _prob:Path = fortune_config.fortune_path / "fortune" / "choice.json"

    with open(_p, "r", encoding="utf-8") as f:
        content = json.load(f).get("copywriting")
    
    with open(_prob, "r", encoding="utf-8") as f:
        probabilities = json.load(f)
        probability = probabilities.get(filename)


    luck = random.choices(content, weights=probability, k=1)

    title: str = luck[0].get("good-luck")
    text: str = random.choice(luck[0].get("content"))

    return title, text


def random_basemap(theme: str, spec_path: Optional[str] = None) -> Tuple[Path, str]:
    if isinstance(spec_path, str):
        p: Path = fortune_config.fortune_path / "img" / spec_path
        filename: str = p.name
        return p, filename

    if theme == "random":
        __p: Path = fortune_config.fortune_path / "img"

        # Each dir is a theme.
        themes: List[str] = [f.name for f in __p.iterdir(
        ) if f.is_dir() and theme_flag_check(f.name)]
        picked: str = random.choice(themes)

        _p: Path = __p / picked
        filename: str = p.name

        # Each file is a posix path of images directory
        images_dir: List[Path] = [i for i in _p.iterdir() if i.is_file()]
        p: Path = random.choice(images_dir)
    else:
        _p: Path = fortune_config.fortune_path / "img" / theme
        images_dir: List[Path] = [i for i in _p.iterdir() if i.is_file()]
        p: Path = random.choice(images_dir)
        filename: str = p.name

    return p, filename


def drawing(gid: str, uid: str, theme: str, spec_path: Optional[str] = None) -> Path:
    # 1. Random choice a base image
    imgPath: Path
    filename_with_extension: str
    imgPath, filename_with_extension = random_basemap(theme, spec_path)
    filename, _ = os.path.splitext(filename_with_extension)
    img: Image.Image = Image.open(imgPath)
    draw = ImageDraw.Draw(img)

    # 2. Random choice a luck text with title
    title, text = get_copywriting()

    # 3. Draw
    font_size = 45
    color = "#F5F5F5"
    image_font_center = [140, 99]
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
    slices, result = decrement(text)

    for i in range(slices):
        font_height: int = len(result[i]) * (font_size + 4)
        textVertical: str = "\n".join(result[i])
        x: int = int(
            image_font_center[0]
            + (slices - 2) * font_size / 2
            + (slices - 1) * 4
            - i * (font_size + 4)
        )
        y: int = int(image_font_center[1] - font_height / 2)
        draw.text((x, y), textVertical, fill=color, font=ttfront)

    # Save
    outDir: Path = fortune_config.fortune_path / "out"
    if not outDir.exists():
        outDir.mkdir(exist_ok=True, parents=True)

    outPath = outDir / f"{gid}_{uid}.png"

    img.save(outPath)
    return outPath


def decrement(text: str) -> Tuple[int, List[str]]:
    '''
            Split the text, return the number of columns and text list
            TODO: Now, it ONLY fit with 2 columns of text
    '''
    length: int = len(text)
    result: List[str] = []
    cardinality = 9
    if length > 4 * cardinality:
        raise Exception

    col_num: int = 1
    while length > cardinality:
        col_num += 1
        length -= cardinality

    # Optimize for two columns
    space = " "
    length = len(text)  # Value of length is changed!

    if col_num == 2:
        if length % 2 == 0:
            # even
            fillIn = space * int(9 - length / 2)
            return col_num, [text[: int(length / 2)] + fillIn, fillIn + text[int(length / 2):]]
        else:
            # odd number
            fillIn = space * int(9 - (length + 1) / 2)
            return col_num, [text[: int((length + 1) / 2)] + fillIn, fillIn + space + text[int((length + 1) / 2):]]

    for i in range(col_num):
        if i == col_num - 1 or col_num == 1:
            result.append(text[i * cardinality:])
        else:
            result.append(text[i * cardinality: (i + 1) * cardinality])

    return col_num, result


def theme_flag_check(theme: str) -> bool:
    '''
            check wether a theme is enabled in themes_flag_config
    '''
    return themes_flag_config.dict().get(theme + "_flag", False)
