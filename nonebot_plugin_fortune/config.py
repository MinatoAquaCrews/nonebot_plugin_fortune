import os
from pydantic import BaseModel

class PluginConfig(BaseModel):
    fortune_path: str = os.path.join(os.path.dirname(__file__), "resource")
    '''
        各主题抽签开关，仅在random抽签中生效
        请确保不全是False
    '''
    arknights_flag: bool = True
    asoul_flag: bool = True
    azure_flag: bool = True
    genshin_flag:  bool = True
    onmyoji_flag: bool = True
    pcr_flag: bool = True
    touhou_flag: bool = True
    touhou_olg_flag: bool = True
    hololive_flag: bool = True
    granblue_fantasy_flag: bool = True
    punishing_flag: bool = True
    pretty_derby_flag: bool = True
    dc4_flag: bool = True
    einstein_flag: bool = True
    sweet_illusion_flag: bool = True
    liqingge_flag: bool = True
    hoshizora_flag: bool = True
    sakura_flag: bool = True 