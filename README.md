<div align="center">

# Fortune

<!-- prettier-ignore-start -->
<!-- markdownlint-disable-next-line MD036 -->
_🙏 今日运势 🙏_
<!-- prettier-ignore-end -->

</div>
<p align="center">
  
  <a href="https://github.com/KafCoppelia/nonebot_plugin_fortune/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/license-MIT-informational">
  </a>
  
  <a href="https://github.com/nonebot/nonebot2">
    <img src="https://img.shields.io/badge/nonebot2-2.0.0beta.1-green">
  </a>
  
  <a href="">
    <img src="https://img.shields.io/badge/release-v0.4.1-orange">
  </a>
  
</p>

</p>

## 版本

v0.4.1 **此版本resource与0.3.x不完全兼容**

⚠ 适配nonebot2-2.0.0beta.1；适配alpha.16参见[alpha.16分支](https://github.com/KafCoppelia/nonebot_plugin_fortune/tree/alpha.16)

[更新日志](https://github.com/KafCoppelia/nonebot_plugin_fortune/releases/tag/v0.4.1)

## 安装

1. 安装方式注意：

    - 通过`pip`或`nb`：pypi无法发行过大安装包，由此安装的插件不包含所有`resource`下所有主题抽签资源，需单独下载，建议`zip`包下载后单独提取`resource`资源，后更改`FORTUNE_PATH`配置即可；
    
    - 通过`zip`或`git clone`安装：包含`resource`下所有主题抽签资源；

2. 抽签签底`img`、字体`font`、文案`fortune`等资源位于`./resource`下，可在`env`下设置`FORTUNE_PATH`更改；

```python
FORTUNE_PATH="your_path_to_resource"   # 默认位于os.path.join(os.path.dirname(__file__), "resource")，具体查看data_source.py
```

3. **新增** 多个galgame的抽签主题，使用了[FloatTech-zbpdata/Fortune](https://github.com/FloatTech/zbpdata)全部主题。在`env`下设置`xxx_FLAG`以启用或关闭抽签随机主题，例如：

```python
ARKNIGHTS_FLAG = true         # 明日方舟
ASOUL_FLAG = false            # A-SOUL
AZURE_FLAG = true             # 碧蓝航线
GENSHIN_FLAG = true           # 原神
ONMYOJI_FLAG = false          # 阴阳师
PCR_FLAG = true               # 公主链接
TOUHOU_FLAG = true            # 东方
TOUHOU_OLD_FLAG = false       # 东方旧版
VTUBER_FLAG = true            # Vtuber
PUNISHING_FLAG = true         # 战双帕弥什
GRANBLUE_FANTASY_FLAG = true  # 碧蓝幻想
PRETTY_DERBY_FLAG = true      # 赛马娘
DC4_FLAG = false              # dc4
EINSTEIN_FLAG = true          # 爱因斯坦携爱敬上
SWEET_ILLUSION_FLAG = true    # 灵感满溢的甜蜜创想
LIQINGGE_FLAG = true          # 李清歌
HOSHIZORA_FLAG = true         # 星空列车与白的旅行
SAKURA_FLAG = true            # 樱色之云绯色之恋
```

**请确保不全为`false`**

4. 在`./resource/fortune_setting.json`内配置**指定抽签**规则，例如：

```json
{
    "group_rule": {
        "123456789": "random",
        "987654321": "azure",
        "123454321": "granblue_fantasy"
    },
    "specific_rule": {
        "凯露": [
            "pcr\/frame_1.jpg",
            "pcr\/frame_2.jpg"
        ],
        "可可萝": [
            "pcr\/frame_41.jpg"
        ]
    }
}
```

*group_rule会自动生成，specific_rule可手动配置*

指定凯露签，由于存在两张凯露的签底，配置凯露签的**路径列表**即可，其余类似，**请确保图片路径、格式输入正确**；

5. 占卜一下你的今日运势！🎉

## 功能

1. 随机抽取今日运势，配置**更多**种抽签主题：原神、PCR、Vtuber、东方、明日方舟、旧版东方、赛马娘、阴阳师、碧蓝航线、碧蓝幻想、战双帕弥什，galgame主题……

2. 可配置随机抽签主题或指定主题，也可指定角色签底（例如可莉、魔理沙、凯露、**阿夸**🥰）；

3. 每群每人一天限抽签1次，0点刷新（贪心的人是不会有好运的🤗）；

4. 抽签的信息会保存在`./resource/fortune_data.json`内；群抽签设置及指定抽签规则保存在`./resource/fortune_setting.json`内；抽签生成的图片当天会保存在`./resource/out`下；

5. **新增** `fortune_setting.json`已预置明日方舟、Asoul、原神、东方、vtb的指定抽签规则；

## 命令

1. 一般抽签：今日运势、抽签、运势；

2. 指定签底并抽签：指定[xxx]签，在`./resource/fortune_setting.json`内手动配置；

3. [群管或群主或超管] 配置抽签主题：

    - 设置[原神/pcr/东方/vtb/xxx]签：设置群抽签主题；

    - 重置抽签：设置群抽签主题为随机；

4. 抽签设置：查看当前群抽签主题的配置；

5. [超管] 刷新抽签：即刻刷新抽签，防止过0点未刷新的意外；

6. 今日运势帮助：显示插件帮助文案；

7. **新增** 主题列表：显示当前已启用主题；

## 效果

测试效果出自群聊。

![display](./display.jpg)

## 本插件改自

[opqqq-plugin](https://github.com/opq-osc/opqqq-plugin)

## 抽签图片及文案资源

1. [opqqq-plugin](https://github.com/opq-osc/opqqq-plugin)：原神、pcr、vtb抽签主题；

2. 感谢江樂丝提供东方签底；

3. [FloatTech-zbpdata/Fortune](https://github.com/FloatTech/zbpdata)：其余主题签；

## 资源整合注意

1. 抽签图片及文案资源下载参见上述出处链接；

2. [FloatTech-zbpdata/Fortune](https://github.com/FloatTech/zbpdata)提供的`text.json`文案资源与[opqqq-plugin](https://github.com/opq-osc/opqqq-plugin)提供的文案资源`copywriting.json`与`goodLuck.json`略有不同，具体不同如下：

	- `text.json`中`title`（吉凶度设定）直接对应`content`（运势文案内容）；

	- 而`goodLuck.json`中`good-luck`（吉凶度编号）对应`name`（吉凶度设定）；`copywriting.json`中`good-luck`（吉凶度编号）对应`content`（运势文案内容）；
