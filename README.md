<div align="center">

# Fortune

<!-- prettier-ignore-start -->
<!-- markdownlint-disable-next-line MD036 -->
_🙏 今日运势 🙏_
<!-- prettier-ignore-end -->

</div>
<p align="center">
  
  <a href="https://github.com/KafCoppelia/nonebot_plugin_fortune/blob/main/LICENSEE">
    <img src="https://img.shields.io/badge/license-MIT-informational">
  </a>
  
  <a href="https://github.com/nonebot/nonebot2">
    <img src="https://img.shields.io/badge/nonebot2-2.0.0alpha.16-green">
  </a>
  
  <a href="">
    <img src="https://img.shields.io/badge/release-v0.2.1-orange">
  </a>
  
</p>

</p>

## 版本

v0.2.1

⚠ 适配nonebot2-2.0.0alpha.16，适配beta.1版本将会放在dev分支。

## 安装

1. 通过`pip`或`nb`安装；

2. 抽签签底`img`、字体`font`、文案`fortune`等资源位于`./resource`下，可在`env`下设置`FORTUNE_PATH`更改；

```python
FORTUNE_PATH="your_path_to_resource"   # 默认位于os.path.join(os.path.dirname(__file__), "resource")，具体查看data_source.py
```

3. 占卜一下你的今日运势！🎉

## 功能

1. 随机抽取今日运势，配置四种抽签主题：原神、PCR、Vtuber、东方；

2. 可设置随机抽签主题或指定主题，也可指定角色签底（例如可莉、魔理沙、凯露、**阿夸**🥰）；

3. 每群每人一天限抽签1次，0点刷新（贪心的人是不会有好运的🤗）；

4. 抽签的信息会保存在`./resource/fortune_data.json`内；群抽签设置保存在`./resource/fortune_setting.json`内；抽签生成的图片当天会保存在`./resource/out`下；

## 命令

1. 一般抽签：今日运势、抽签、运势；

2. 指定签底并抽签：指定[xxx]签，具体配置位于`utils.py`下`SpecificTypeList`；

3. 配置抽签主题（有权限）：
    - 设置[原神/pcr/东方/vtb]签：设置群抽签主题；

    - 重置抽签：设置群抽签主题为随机；

4. 抽签设置：查看当前群抽签主题的配置；

## 效果

测试效果出自群聊。

![display](./display.jpg)

## 本插件改自：

1. [opqqq-plugin](https://github.com/opq-osc/opqqq-plugin)，除功能函数外，由于要适配nonebot2，底层已大改；

2. 感谢江樂丝提供东方签底~~实际上可能是东方老哥提供的~~；