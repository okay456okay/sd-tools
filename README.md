# AI绘画工具合集

自己在用的一些AI绘画相关的工具和脚本合集。

## 安装部署

```shell
pip install -r requirements.txt
```

然后按下面的指引使用对应的工具或脚本即可。

## Stable Diffusion WebUI

## Civitai

### Civitai 获取图片脚本 download_civitai_images.py

从 Civitai 网站获取图片，并将图片生成信息保存到了图片里，在 Stable Diffusion WebUI 中一键还原。 

使用方法：
```shell
python download_civitai_images.py -h|--help  # 查看帮助
python download_civitai_images.py  # 默认获取配置文件中所有模型当天按评论数前100张图片
```