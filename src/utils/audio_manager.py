"""
三国霸业游戏 - 音频管理器
统一管理游戏音效和背景音乐
"""

import pygame
from utils.asset_manager import asset_manager
from utils.logger import get_logger

logger = get_logger('audio_manager')


class AudioManager:
    """音频管理器 - 管理游戏音效和音乐"""

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

        # 音频是否可用
        self._audio_available = False

        # 初始化音频系统
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self._audio_available = True
            logger.info("音频系统初始化完成")
        except Exception as e:
            logger.warning(f"音频系统初始化失败，游戏将继续运行但无音效: {e}")

        # 音量设置 (0.0 - 1.0)
        self._sound_volume = 0.7
        self._music_volume = 0.5
        self._muted = False

        # 当前播放的音乐
        self._current_music = None

        # 音效缓存
        self._sounds = {}

        # 设置默认音量
        if self._audio_available:
            self._apply_volumes()

    def _apply_volumes(self):
        """应用音量设置"""
        if not self._audio_available:
            return
        if not self._muted:
            pygame.mixer.music.set_volume(self._music_volume)
        else:
            pygame.mixer.music.set_volume(0)

    def play_sound(self, sound_name: str, volume: float = None):
        """播放音效

        Args:
            sound_name: 音效名称
            volume: 音量覆盖 (0.0-1.0)
        """
        if not self._audio_available or self._muted:
            return

        try:
            # 从资源管理器加载音效
            sound = asset_manager.load_audio(f"{sound_name}.wav")
            if sound is None:
                sound = asset_manager.load_audio(f"{sound_name}.ogg")
            if sound is None:
                sound = asset_manager.load_audio(f"{sound_name}.mp3")

            if sound:
                vol = volume if volume is not None else self._sound_volume
                sound.set_volume(vol)
                sound.play()
                logger.debug(f"播放音效: {sound_name}")
            else:
                logger.debug(f"音效不存在: {sound_name}")
        except Exception as e:
            logger.error(f"播放音效失败 {sound_name}: {e}")

    def play_music(self, music_name: str, loops: int = -1, fade_ms: int = 500):
        """播放背景音乐

        Args:
            music_name: 音乐名称
            loops: 循环次数，-1为无限循环
            fade_ms: 淡入时间（毫秒）
        """
        if not self._audio_available:
            return

        if self._current_music == music_name:
            return

        try:
            # 尝试不同格式
            formats = ['.mp3', '.ogg', '.wav']
            music_path = None

            for fmt in formats:
                from utils.constants import AUDIO_DIR
                import os
                path = os.path.join(AUDIO_DIR, f"{music_name}{fmt}")
                if os.path.exists(path):
                    music_path = path
                    break

            if music_path:
                pygame.mixer.music.fadeout(fade_ms)
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(self._music_volume if not self._muted else 0)
                pygame.mixer.music.play(loops, fade_ms=fade_ms)
                self._current_music = music_name
                logger.info(f"播放音乐: {music_name}")
            else:
                logger.debug(f"音乐不存在: {music_name}")
        except Exception as e:
            logger.error(f"播放音乐失败 {music_name}: {e}")

    def stop_music(self, fade_ms: int = 500):
        """停止背景音乐"""
        if not self._audio_available:
            return
        try:
            pygame.mixer.music.fadeout(fade_ms)
            self._current_music = None
            logger.debug("停止音乐")
        except Exception as e:
            logger.error(f"停止音乐失败: {e}")

    def pause_music(self):
        """暂停背景音乐"""
        if not self._audio_available:
            return
        try:
            pygame.mixer.music.pause()
            logger.debug("暂停音乐")
        except Exception as e:
            logger.error(f"暂停音乐失败: {e}")

    def resume_music(self):
        """恢复背景音乐"""
        if not self._audio_available or self._muted:
            return
        try:
            pygame.mixer.music.unpause()
            logger.debug("恢复音乐")
        except Exception as e:
            logger.error(f"恢复音乐失败: {e}")

    def set_sound_volume(self, volume: float):
        """设置音效音量

        Args:
            volume: 音量 0.0-1.0
        """
        self._sound_volume = max(0.0, min(1.0, volume))
        logger.debug(f"音效音量: {self._sound_volume}")

    def set_music_volume(self, volume: float):
        """设置音乐音量

        Args:
            volume: 音量 0.0-1.0
        """
        self._music_volume = max(0.0, min(1.0, volume))
        if self._audio_available:
            self._apply_volumes()
        logger.debug(f"音乐音量: {self._music_volume}")

    def get_sound_volume(self) -> float:
        """获取音效音量"""
        return self._sound_volume

    def get_music_volume(self) -> float:
        """获取音乐音量"""
        return self._music_volume

    def mute(self):
        """静音"""
        self._muted = True
        pygame.mixer.music.set_volume(0)
        logger.debug("静音")

    def unmute(self):
        """取消静音"""
        self._muted = False
        self._apply_volumes()
        logger.debug("取消静音")

    def is_muted(self) -> bool:
        """是否静音"""
        return self._muted

    def toggle_mute(self):
        """切换静音状态"""
        if self._muted:
            self.unmute()
        else:
            self.mute()

    def stop_all_sounds(self):
        """停止所有音效"""
        if not self._audio_available:
            return
        try:
            pygame.mixer.stop()
            logger.debug("停止所有音效")
        except Exception as e:
            logger.error(f"停止音效失败: {e}")


# 全局音频管理器实例
audio_manager = AudioManager()


# 音效名称常量
class SoundEffects:
    """音效名称常量"""
    BUTTON_CLICK = "button_click"
    BUTTON_HOVER = "button_hover"
    MENU_OPEN = "menu_open"
    MENU_CLOSE = "menu_close"
    TURN_END = "turn_end"
    BATTLE_START = "battle_start"
    BATTLE_WIN = "battle_win"
    BATTLE_LOSE = "battle_lose"
    CITY_CAPTURE = "city_capture"
    DIPLOMACY_SUCCESS = "diplomacy_success"
    DIPLOMACY_FAIL = "diplomacy_fail"
    RECRUIT = "recruit"
    LEVEL_UP = "level_up"


class MusicTracks:
    """音乐名称常量"""
    MAIN_MENU = "main_menu"
    WORLD_MAP = "world_map"
    BATTLE = "battle"
    CITY = "city"
    VICTORY = "victory"
    DEFEAT = "defeat"
