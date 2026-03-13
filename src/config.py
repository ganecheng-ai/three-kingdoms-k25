"""
三国霸业游戏 - 配置管理
"""

import json
import os
from utils.logger import get_logger

logger = get_logger('config')

# 默认配置
DEFAULT_CONFIG = {
    'display': {
        'width': 1280,
        'height': 720,
        'fullscreen': False,
        'fps': 60,
    },
    'audio': {
        'music_volume': 0.5,
        'sound_volume': 0.7,
        'enable_music': True,
        'enable_sound': True,
    },
    'game': {
        'difficulty': 'normal',  # easy, normal, hard
        'auto_save': True,
        'auto_save_interval': 300,  # 秒
        'language': 'zh_CN',
    },
    'debug': {
        'show_fps': False,
        'enable_console': False,
    }
}

CONFIG_FILE = 'config.json'


class Config:
    """配置管理类"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._config = DEFAULT_CONFIG.copy()
        self.load()

    def load(self):
        """加载配置文件"""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    self._deep_update(self._config, loaded)
                logger.info(f"配置文件加载成功: {CONFIG_FILE}")
            except Exception as e:
                logger.error(f"加载配置文件失败: {e}")
                self.save()  # 保存默认配置
        else:
            logger.info("配置文件不存在，使用默认配置")
            self.save()

    def save(self):
        """保存配置文件"""
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=4, ensure_ascii=False)
            logger.info(f"配置文件保存成功: {CONFIG_FILE}")
        except Exception as e:
            logger.error(f"保存配置文件失败: {e}")

    def _deep_update(self, base_dict, update_dict):
        """深度更新字典"""
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value

    def get(self, key_path, default=None):
        """获取配置值（支持点号路径）"""
        keys = key_path.split('.')
        value = self._config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

    def set(self, key_path, value):
        """设置配置值（支持点号路径）"""
        keys = key_path.split('.')
        config = self._config
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        config[keys[-1]] = value
        self.save()

    def get_display_size(self):
        """获取显示尺寸"""
        return (self.get('display.width'), self.get('display.height'))


# 全局配置实例
config = Config()
