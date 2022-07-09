from pathlib import Path
import ujson as json
import random

pa = Path(__file__).parent / "resource"

def random_pick_theme() -> str:
    '''
        Random choose a theme, and check whether is enable
    '''
    _config_path: Path = pa / "fortune_config.json"
    with open(_config_path, "r", encoding="utf-8") as f:
        _d = json.load(f)
    
    while True:
        picked: str = random.choice(list(_d))
        if _d.get(picked, False) is True:
            return picked.split("_flag")[0]
        
print(random_pick_theme())