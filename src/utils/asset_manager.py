"""
三国霸业游戏 - 资源加载管理器
"""

import os
import pygame
from pathlib import Path
from utils.constants import (
    IMAGES_DIR, FONTS_DIR, AUDIO_DIR,
    ASSETS_DIR
)
from utils.logger import get_logger

logger = get_logger('asset_manager')


class AssetManager:
    """资源加载管理器 - 统一管理游戏资源的加载和缓存"""

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

        # 资源缓存
        self._images = {}
        self._fonts = {}
        self._audio = {}

        # 确保资源目录存在
        self._ensure_directories()

        logger.info("资源管理器初始化完成")

    def _ensure_directories(self):
        """确保资源目录存在"""
        dirs = [ASSETS_DIR, IMAGES_DIR, FONTS_DIR, AUDIO_DIR]
        for dir_path in dirs:
            if not os.path.exists(dir_path):
                try:
                    os.makedirs(dir_path)
                    logger.info(f"创建资源目录: {dir_path}")
                except Exception as e:
                    logger.error(f"创建目录失败 {dir_path}: {e}")

    def load_image(self, filename, use_cache=True):
        """加载图片资源

        Args:
            filename: 图片文件名
            use_cache: 是否使用缓存

        Returns:
            pygame.Surface: 加载的图片，失败返回None
        """
        if use_cache and filename in self._images:
            return self._images[filename]

        filepath = os.path.join(IMAGES_DIR, filename)
        try:
            if os.path.exists(filepath):
                image = pygame.image.load(filepath).convert_alpha()
                if use_cache:
                    self._images[filename] = image
                logger.debug(f"加载图片: {filename}")
                return image
            else:
                logger.warning(f"图片不存在: {filepath}")
                return None
        except Exception as e:
            logger.error(f"加载图片失败 {filename}: {e}")
            return None

    def load_font(self, filename, size, use_cache=True):
        """加载字体

        Args:
            filename: 字体文件名
            size: 字体大小
            use_cache: 是否使用缓存

        Returns:
            pygame.font.Font: 加载的字体，失败返回系统默认字体
        """
        cache_key = f"{filename}_{size}"
        if use_cache and cache_key in self._fonts:
            return self._fonts[cache_key]

        filepath = os.path.join(FONTS_DIR, filename)
        try:
            if os.path.exists(filepath):
                font = pygame.font.Font(filepath, size)
                if use_cache:
                    self._fonts[cache_key] = font
                logger.debug(f"加载字体: {filename} ({size}px)")
                return font
            else:
                logger.warning(f"字体不存在: {filepath}")
                return pygame.font.SysFont('simhei', size)
        except Exception as e:
            logger.error(f"加载字体失败 {filename}: {e}")
            return pygame.font.SysFont('simhei', size)

    def get_font(self, size, filename=None):
        """获取字体

        Args:
            size: 字体大小
            filename: 字体文件名，None则使用系统字体

        Returns:
            pygame.font.Font: 字体对象
        """
        if filename:
            return self.load_font(filename, size)
        else:
            # 尝试加载系统默认中文字体
            system_fonts = [
                '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
                '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
                '/System/Library/Fonts/PingFang.ttc',
                'C:/Windows/Fonts/simhei.ttf',
                'C:/Windows/Fonts/msyh.ttc',
            ]
            for font_path in system_fonts:
                if os.path.exists(font_path):
                    cache_key = f"system_{font_path}_{size}"
                    if cache_key in self._fonts:
                        return self._fonts[cache_key]
                    try:
                        font = pygame.font.Font(font_path, size)
                        self._fonts[cache_key] = font
                        return font
                    except:
                        continue
            # 回退到系统字体
            return pygame.font.SysFont('simhei', size)

    def load_audio(self, filename, use_cache=True):
        """加载音频资源

        Args:
            filename: 音频文件名
            use_cache: 是否使用缓存

        Returns:
            pygame.mixer.Sound: 加载的音频，失败返回None
        """
        if use_cache and filename in self._audio:
            return self._audio[filename]

        filepath = os.path.join(AUDIO_DIR, filename)
        try:
            if os.path.exists(filepath):
                sound = pygame.mixer.Sound(filepath)
                if use_cache:
                    self._audio[filename] = sound
                logger.debug(f"加载音频: {filename}")
                return sound
            else:
                logger.warning(f"音频不存在: {filepath}")
                return None
        except Exception as e:
            logger.error(f"加载音频失败 {filename}: {e}")
            return None

    def play_sound(self, filename, loops=0):
        """播放音效

        Args:
            filename: 音效文件名
            loops: 循环次数，-1为无限循环
        """
        sound = self.load_audio(filename)
        if sound:
            sound.play(loops=loops)
            logger.debug(f"播放音效: {filename}")

    def play_music(self, filename, loops=-1, volume=0.5):
        """播放背景音乐

        Args:
            filename: 音乐文件名
            loops: 循环次数，-1为无限循环
            volume: 音量 0.0-1.0
        """
        filepath = os.path.join(AUDIO_DIR, filename)
        try:
            if os.path.exists(filepath):
                pygame.mixer.music.load(filepath)
                pygame.mixer.music.set_volume(volume)
                pygame.mixer.music.play(loops)
                logger.info(f"播放音乐: {filename}")
            else:
                logger.warning(f"音乐不存在: {filepath}")
        except Exception as e:
            logger.error(f"播放音乐失败 {filename}: {e}")

    def stop_music(self):
        """停止音乐"""
        pygame.mixer.music.stop()
        logger.debug("停止音乐")

    def create_placeholder_image(self, width, height, color, filename=None):
        """创建占位图片

        Args:
            width: 宽度
            height: 高度
            color: 颜色
            filename: 如果提供，保存到该文件名

        Returns:
            pygame.Surface: 创建的图像
        """
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        surface.fill(color)

        if filename:
            filepath = os.path.join(IMAGES_DIR, filename)
            try:
                pygame.image.save(surface, filepath)
                logger.info(f"创建占位图片: {filepath}")
            except Exception as e:
                logger.error(f"保存图片失败: {e}")

        return surface

    def clear_cache(self, resource_type=None):
        """清除缓存

        Args:
            resource_type: 'images', 'fonts', 'audio' 或 None(全部)
        """
        if resource_type is None or resource_type == 'images':
            self._images.clear()
            logger.debug("清除图片缓存")

        if resource_type is None or resource_type == 'fonts':
            self._fonts.clear()
            logger.debug("清除字体缓存")

        if resource_type is None or resource_type == 'audio':
            self._audio.clear()
            logger.debug("清除音频缓存")

    def get_cache_info(self):
        """获取缓存信息

        Returns:
            dict: 缓存统计信息
        """
        return {
            'images': len(self._images),
            'fonts': len(self._fonts),
            'audio': len(self._audio),
        }


# 全局资源管理器实例
asset_manager = AssetManager()
