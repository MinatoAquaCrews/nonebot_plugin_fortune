## 如何添加更多的抽签主题资源？

1. 将新的主题目录放置在 `./img` 下；

2. 修改 `config.py` 中的 `ThemesFlagConfig`，添加 `new_theme_flag` 标志，例如：

   ```python
   ...
   touhou_flag: bool = True
   new_theme_flag: bool = True
   ...
   ```

   之后可在 `.env` 下设置以启用或关闭该主题：

   ```python
   NEW_THEME_FLAG=true
   ```

3. 修改 `utils.py` 中的 `FortuneThemesDict`，添加键值对：

   ```python
   ...
   "touhou":   ["东方", "touhou", "Touhou", "车万"],
   "new_theme":["新主题", "新的主题"],
   ...
   ```

   添加位置不一定在此，仅举例。

4. 重新启动插件即可。Enjoy!🥳
