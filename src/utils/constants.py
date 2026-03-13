"""
三国霸业游戏 - 工具函数和常量定义
"""

import os

# 屏幕设置
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# 颜色定义
COLORS = {
    'black': (0, 0, 0),
    'white': (255, 255, 255),
    'red': (255, 0, 0),
    'green': (0, 255, 0),
    'blue': (0, 0, 255),
    'yellow': (255, 255, 0),
    'purple': (128, 0, 128),
    'orange': (255, 165, 0),
    'gray': (128, 128, 128),
    'dark_gray': (64, 64, 64),
    'light_gray': (192, 192, 192),
    'brown': (139, 69, 19),
    'gold': (255, 215, 0),
    'dark_red': (139, 0, 0),
    'dark_green': (0, 100, 0),
    'dark_blue': (0, 0, 139),
    # 游戏主题色
    'primary': (139, 69, 19),       # 主色（棕色）
    'secondary': (255, 215, 0),     # 次色（金色）
    'background': (245, 222, 179),  # 背景色（小麦色）
    'panel_bg': (255, 248, 220),    # 面板背景（玉米丝色）
    'text': (60, 40, 20),           # 文字颜色
    'text_light': (255, 248, 220),  # 浅色文字
    'border': (101, 67, 33),        # 边框色
    'highlight': (255, 223, 128),   # 高亮色
    'disabled': (169, 169, 169),    # 禁用色
}

# 场景类型
SCENE_MENU = 'menu'
SCENE_WORLD_MAP = 'world_map'
SCENE_CITY = 'city'
SCENE_BATTLE = 'battle'
SCENE_OFFICER = 'officer'
SCENE_SETTINGS = 'settings'

# 游戏状态
GAME_STATE_MENU = 'menu'
GAME_STATE_PLAYING = 'playing'
GAME_STATE_PAUSED = 'paused'
GAME_STATE_BATTLE = 'battle'
GAME_STATE_OVER = 'over'

# 路径设置
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
IMAGES_DIR = os.path.join(ASSETS_DIR, 'images')
FONTS_DIR = os.path.join(ASSETS_DIR, 'fonts')
AUDIO_DIR = os.path.join(ASSETS_DIR, 'audio')
LOGS_DIR = os.path.join(BASE_DIR, '..', 'logs')

def get_asset_path(asset_type, filename):
    """获取资源文件路径"""
    if asset_type == 'image':
        return os.path.join(IMAGES_DIR, filename)
    elif asset_type == 'font':
        return os.path.join(FONTS_DIR, filename)
    elif asset_type == 'audio':
        return os.path.join(AUDIO_DIR, filename)
    return None

def ensure_dir(path):
    """确保目录存在"""
    if not os.path.exists(path):
        os.makedirs(path)

# 势力颜色
FACTION_COLORS = {
    0: (128, 128, 128),    # 中立
    1: (255, 0, 0),        # 魏 - 红
    2: (0, 128, 0),        # 蜀 - 绿
    3: (0, 0, 255),        # 吴 - 蓝
    4: (255, 255, 0),      # 黄巾 - 黄
    5: (128, 0, 128),      # 董卓 - 紫
    6: (255, 165, 0),      # 袁绍 - 橙
    7: (0, 255, 255),      # 其他
}

# 地形类型
TERRAIN_PLAIN = 'plain'
TERRAIN_MOUNTAIN = 'mountain'
TERRAIN_FOREST = 'forest'
TERRAIN_WATER = 'water'
TERRAIN_ROAD = 'road'
TERRAIN_CITY = 'city'

TERRAIN_COLORS = {
    TERRAIN_PLAIN: (144, 238, 144),      # 浅绿色
    TERRAIN_MOUNTAIN: (139, 69, 19),     # 棕色
    TERRAIN_FOREST: (34, 139, 34),       # 深绿色
    TERRAIN_WATER: (65, 105, 225),       # 宝蓝色
    TERRAIN_ROAD: (210, 180, 140),       # 棕褐色
    TERRAIN_CITY: (255, 215, 0),         # 金色
}
