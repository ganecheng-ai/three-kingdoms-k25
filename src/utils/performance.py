"""
三国霸业游戏 - 性能优化模块
提供各种性能优化功能
"""

import pygame
from utils.logger import get_logger

logger = get_logger('performance')


class PerformanceOptimizer:
    """性能优化器"""

    def __init__(self):
        self.frame_times = []
        self.max_frame_history = 60
        self._dirty_rects = []
        self._use_dirty_rects = False
        self._fps_limit = 60

    def update_frame_time(self, dt: float):
        """更新帧时间记录"""
        self.frame_times.append(dt)
        if len(self.frame_times) > self.max_frame_history:
            self.frame_times.pop(0)

    def get_average_fps(self) -> float:
        """获取平均FPS"""
        if not self.frame_times:
            return 0.0
        avg_dt = sum(self.frame_times) / len(self.frame_times)
        if avg_dt <= 0:
            return 0.0
        return 1.0 / avg_dt

    def get_performance_stats(self) -> dict:
        """获取性能统计"""
        if not self.frame_times:
            return {'fps': 0, 'avg_dt': 0, 'min_dt': 0, 'max_dt': 0}

        return {
            'fps': self.get_average_fps(),
            'avg_dt': sum(self.frame_times) / len(self.frame_times) * 1000,  # ms
            'min_dt': min(self.frame_times) * 1000,
            'max_dt': max(self.frame_times) * 1000,
        }

    def enable_dirty_rects(self, enable: bool = True):
        """启用脏矩形优化"""
        self._use_dirty_rects = enable
        if enable:
            logger.info("脏矩形优化已启用")
        else:
            logger.info("脏矩形优化已禁用")

    def add_dirty_rect(self, rect):
        """添加脏矩形"""
        if self._use_dirty_rects:
            self._dirty_rects.append(rect)

    def get_dirty_rects(self):
        """获取脏矩形列表"""
        rects = self._dirty_rects.copy()
        self._dirty_rects.clear()
        return rects


class RenderCache:
    """渲染缓存 - 缓存静态元素的渲染结果"""

    def __init__(self):
        self._cache = {}
        self._cache_hits = 0
        self._cache_misses = 0

    def get(self, key: str):
        """获取缓存"""
        if key in self._cache:
            self._cache_hits += 1
            return self._cache[key]
        self._cache_misses += 1
        return None

    def set(self, key: str, surface):
        """设置缓存"""
        self._cache[key] = surface

    def clear(self, key: str = None):
        """清除缓存"""
        if key is None:
            self._cache.clear()
        elif key in self._cache:
            del self._cache[key]

    def get_stats(self) -> dict:
        """获取缓存统计"""
        total = self._cache_hits + self._cache_misses
        hit_rate = self._cache_hits / total if total > 0 else 0
        return {
            'hits': self._cache_hits,
            'misses': self._cache_misses,
            'hit_rate': hit_rate,
            'size': len(self._cache),
        }


class LazyLoader:
    """延迟加载器 - 按需加载资源"""

    def __init__(self, loader_func):
        self._loader_func = loader_func
        self._loaded = False
        self._value = None

    @property
    def value(self):
        """获取值（延迟加载）"""
        if not self._loaded:
            self._value = self._loader_func()
            self._loaded = True
        return self._value

    def reload(self):
        """重新加载"""
        self._loaded = False
        self._value = None


def optimize_surface(surface: pygame.Surface) -> pygame.Surface:
    """优化Surface以加快渲染

    Args:
        surface: 原始Surface

    Returns:
        优化后的Surface
    """
    try:
        # 转换为 fastest 格式
        optimized = surface.convert_alpha()
        return optimized
    except Exception as e:
        logger.warning(f"Surface优化失败: {e}")
        return surface


def clip_surface(surface: pygame.Surface, rect: pygame.Rect) -> pygame.Surface:
    """裁剪Surface

    Args:
        surface: 原始Surface
        rect: 裁剪区域

    Returns:
        裁剪后的Surface
    """
    try:
        clipped = surface.subsurface(rect).copy()
        return clipped
    except Exception as e:
        logger.warning(f"Surface裁剪失败: {e}")
        return surface


def create_optimized_font(name: str, size: int):
    """创建优化的字体

    Args:
        name: 字体名称
        size: 字体大小

    Returns:
        字体对象
    """
    try:
        import os
        from utils.constants import FONTS_DIR

        # 尝试加载字体文件
        font_path = os.path.join(FONTS_DIR, name)
        if os.path.exists(font_path):
            return pygame.font.Font(font_path, size)

        # 回退到系统字体
        return pygame.font.SysFont(name, size)
    except Exception as e:
        logger.warning(f"字体创建失败: {e}")
        return pygame.font.Font(None, size)


# 全局性能优化器实例
performance_optimizer = PerformanceOptimizer()
render_cache = RenderCache()
