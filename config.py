import logging
import os.path

PROXIES = {
    'http': 'http://127.0.0.1:7890',
    'https': 'http://127.0.0.1:7890'
}

LOG_LEVEL = logging.INFO
LOG_FILE = os.path.join('logs', 'sd-tools.log')

# 下载 Civitai图片相关配置
CIVITAI_IMAGES_DIR = 'civitai_images'
CIVITAI_API = 'https://civitai.com/api'
MODELS = [None, 6424, 47130, 13113, 43331, 43977, 47274, 9139, 4023, 35544, 12975, 25494, 10415, 16599, 8281,
          14605, 20942, 78605, 7279, 5041, 10028, 11031, 6841, 7479,
          16677, 78754, 33208, 26124, 12657, 9025, 14171, 8484, 10850, 53601, 13125, 11722, 19239, 18809,
          8217, 15271,
          14978, 16274, 16599, 18427, 20632, 2661, 27259, 4201, 4384, 4468, 4629, 4823, 5041, 6526, 6638,
          6755, 9942,
          ]
LIKE = 5
HEART = 5
LAUGH = 5
DISLIKE = 10
DISCARD_NO_META = True  # 丢弃没有meta信息的图片
