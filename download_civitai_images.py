"""
下载 Civitai 图片
"""
import datetime
import argparse
import sys
from time import sleep

import requests
import json
import os
from log import logger
from PIL import Image, PngImagePlugin
from PIL import ImageFile

from config import PROXIES, MODELS, CIVITAI_IMAGES_DIR, CIVITAI_API, DISCARD_NO_META
from config import LIKE, LAUGH, HEART, DISLIKE

ImageFile.LOAD_TRUNCATED_IMAGES = True

s = requests.session()
s.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.57Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.57',
    'Content-Type': 'application/json'
})
s.proxies = PROXIES


def download_image(url: str, file: str, override: bool = False):
    """
    下载图片
    :param url: 图片url
    :param file: 图文保存路径
    :param override: 是否覆盖
    :return: True 下载成功，False 下载失败
    """
    if not override:
        if os.path.exists(file):
            logger.info(f"{file} already exists, skip")
            return False
    while True:
        try:
            logger.info(f"start download image: {file}")
            r = s.get(url, stream=True)
            with open(file, 'wb') as f:
                for data in r.iter_content(128):
                    f.write(data)
            logger.info(f"finish download image: {file}")
            return True
        except Exception as e:
            logger.info(f"download image: {file} error: {e}")
            sleep(1)


def save_to_png(jpeg_image_path: str, png_image_path: str, info: dict):
    """
    将 jpg 图片保存为 png图片
    :param jpeg_image_path: jpg图片路径
    :param png_image_path: png图片路径
    :param info: 图片信息
    :return:
    """
    # 打开 JPEG 图片
    # png_image_path = os.path.join(os.path.dirname(jpeg_image_path),
    #                               f"{os.path.basename(jpeg_image_path).split('.')[0]}.png")
    try:
        jpeg_image = Image.open(jpeg_image_path)
    except Exception as e:
        logger.warning(f"Open jpeg image failed: {jpeg_image_path}")
        return

    # 创建一个新的 RGBA 图像对象
    png_image = Image.new("RGBA", jpeg_image.size)

    # 将 JPEG 图片复制到 RGBA 图像中
    png_image.paste(jpeg_image, (0, 0))

    # 添加 PNGinfo
    pnginfo = PngImagePlugin.PngInfo()
    # pnginfo.add_text("parameters", json.dumps(info))
    pnginfo.add_text("parameters", info)

    # 保存 PNG 图像
    # print(png_image_path)
    png_image.save(png_image_path, "PNG", pnginfo=pnginfo)

    # 关闭图像对象
    jpeg_image.close()
    png_image.close()
    logger.info(f"save png image: {png_image_path}")
    return png_image_path


def save_image(image_info: dict, save_dir: str, discard_no_meta=DISCARD_NO_META):
    """
    保存图片
    :param image_info:
    :param save_dir:
    :param discard_no_meta 是否丢弃掉没有包含meta的图片
    :return:
    """
    image_id = str(image_info.get('id'))
    meta = image_info.get('meta', {})
    info = {'fullInfo': image_info}
    if meta:
        info['prompt'] = meta.get('prompt', '')
        info['negativePrompt'] = meta.get('negativePrompt', '')
        info['ENSD'] = meta.get('ENSD', '31999')
        info['Steps'] = meta.get('steps', 0)
        info['Sampler'] = meta.get('sampler', '')
        info['Seed'] = meta.get('seed', -1)
        info['Size'] = meta.get('Size', '512x512')
        info['Width'], info['Height'] = info['Size'].split('x')
        info['Model hash'] = meta.get('Model hash', '')
        info['Model'] = meta.get('Model', '')
        info['CFG scale'] = meta.get('cfgScale', 7)
        info['Denoising strength'] = meta.get('Denoising strength', 0.4)
        info['Clip skip'] = meta.get('Clip skip', 2)
        info['Hires steps'] = meta.get('Hires steps', 0)
        info['Hires upscale'] = meta.get('Hires upscale', '')
        info['Hires upscaler'] = meta.get('Hires upscaler', '')
        png_image_path = os.path.join(save_dir,
                                      f"meta_{image_info.get('nsfwLevel', 'None')}_{info['Model']}_{image_id}.png")
    else:
        if discard_no_meta:
            return
        png_image_path = os.path.join(save_dir, f"no_meta_{image_info.get('nsfwLevel', 'None')}_{image_id}.png")
    if os.path.exists(png_image_path):
        logger.info(f"{png_image_path} already exists, skip")
        return
    image_url = image_info.get('url')
    jpeg_image_path = os.path.join(save_dir, f"civitai_{image_id}.jpeg")
    if os.path.exists(jpeg_image_path) and os.path.getsize(jpeg_image_path) / 1024 / 1024 > 8:
        return
    download_image(image_url, jpeg_image_path)
    if os.path.getsize(jpeg_image_path) / 1024 / 1024 > 8:
        return
    info_str = f"""{info.get('prompt', '')}
Negative prompt: {info.get('negativePrompt', '')}
{', '.join([f"{k}: {v}" for k, v in info.items() if k not in ['prompt', 'negativePrompt', 'fullInfo']])}
"""
    if save_to_png(jpeg_image_path, png_image_path, info_str):
        os.remove(jpeg_image_path)


def get_images(save_dir, model_id=None, limit=10, page=1, sort="Most Reactions", period='Day', nsfw=None):
    """
    获取模型图片信息
    :param save_dir
    :param model_id
    :param limit
    :param page
    :param period enum (AllTime, Year, Month, Week, Day)
    :param sort enum (Most Reactions, Most Comments, Newest)
    :param nsfw boolean | enum (None, Soft, Mature, X)
    """
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
    params = {
        'limit': limit,
        # 'page': page,
        "sort": sort,
        "period": period,
        # "nsfw": 'None',
    }
    if nsfw:
        params['nsfw'] = nsfw
    if model_id:
        params['modelId'] = model_id
    for i in range(1, page + 1):
        params['page'] = i
        logger.info(
            f"download images, model: {model_id}, period: {period}, nsfw: {nsfw}, download page: {i}, limit: {limit}")
        while True:
            try:
                r = s.get(url=f"{CIVITAI_API}/v1/images", params=params, timeout=120)
                images = r.json().get('items', [])
                break
            except Exception as e:
                logger.warning(f"get images list failed, {json.dumps(params)}, error: {e}")
                sleep(5)
        for image in images:
            laugh = image.get('stats', {}).get("laughCount", 0)
            like = image.get('stats', {}).get("likeCount", 0)
            heart = image.get('stats', {}).get("heartCount", 0)
            dislike = image.get('stats', {}).get("dislikeCount", 0)
            comment = image.get('stats', {}).get("dislikeCount", 0)
            if (not (laugh >= LAUGH or like >= LIKE or heart >= HEART)) or dislike >= DISLIKE:
                continue
            save_image(image, save_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="download civitai images arguments")
    parser.add_argument('--period', type=str, default='Day', help="AllTime, Year, Month, Week, Day, 默认: Day")
    parser.add_argument('--nsfw', type=str, default="", help="Soft, Mature, X, '', ''表示包含所有级别, 默认: 所有级别")
    parser.add_argument('--page', type=int, default=1, help="要获取多少页, 默认: 1")
    parser.add_argument('--limit', type=int, default=100, help="每页多少张, 默认: 50")
    parser.add_argument('--sort', type=str, default="Most Reaction",
                        help="Most Reactions, Most Comments, Newest, 默认: Most Reactions")
    args = parser.parse_args()
    save_dir = os.path.join(CIVITAI_IMAGES_DIR)
    for model_id in MODELS:
        get_images(save_dir=save_dir, model_id=model_id, page=args.page, limit=args.limit, period=args.period,
                   nsfw=args.nsfw)
