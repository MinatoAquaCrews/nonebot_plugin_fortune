## 如何在`v0.4.2`或更早版本上更新抽签主题资源？

`v0.4.3`新增东方归言录(touhou_lostword)全新抽签主题资源！

1. 将新资源文件夹放置在`./img`下；

2. 修改`config.py`配置的项目，添加`touhou_lostword_flag`以启用或关闭该主题，例如新增至：

    ```python
    ...
    touhou_flag: bool = True
    touhou_lostword_flag: bool = True
    touhou_olg_flag: bool = True
    ...
    ```

    之后可在`.env`下设置：

    ```python
    TOUHOU_LOSTWORD_FLAG=true   # 东方归言录，东方DLC
    ```

3. 修改`utils.py`的`MainThemeEnable`，添加键`"touhou_lostword"`：

    从
    ```python 
    ...
    "touhou":           config.touhou_flag,
    "touhou_old":       config.touhou_olg_flag,
    ...
    ```
    至
    ```python 
    ...
    "touhou":           config.touhou_flag,
    "touhou_lostword":  config.touhou_lostword_flag,
    "touhou_old":       config.touhou_olg_flag,
    ...
    ```
    添加位置不一定在此，仅举例。

4. 修改`utils.py`的`MainThemeList`，添加键值对：

    从
    ```python
    ...
    "touhou":   ["东方", "touhou", "Touhou", "车万"],
    "touhou_old": 
                ["旧东方", "旧版东方", "老东方", "老版东方", "经典东方"],
    ...
    ```
    至
    ```python
    ...
    "touhou":   ["东方", "touhou", "Touhou", "车万"],
    "touhou_lostword": 
                ["东方归言录", "东方lostword", "touhou lostword", "Touhou dlc"],
    "touhou_old": 
                ["旧东方", "旧版东方", "老东方", "老版东方", "经典东方"],
    ...
    ```
    添加位置不一定在此，仅举例。

5. Enjoy!🥳