"""
三国霸业游戏 - 动画系统
提供各种UI动画效果
"""

import pygame
from typing import Callable, Optional, Any
from utils.logger import get_logger

logger = get_logger('animation')


class Animation:
    """动画基类"""

    def __init__(self, duration: float, easing: str = 'linear'):
        """初始化动画

        Args:
            duration: 动画持续时间（秒）
            easing: 缓动函数类型 ('linear', 'ease_in', 'ease_out', 'ease_in_out', 'bounce')
        """
        self.duration = duration
        self.easing = easing
        self.elapsed = 0.0
        self.finished = False
        self.on_complete: Optional[Callable] = None

    def update(self, dt: float):
        """更新动画状态"""
        if self.finished:
            return

        self.elapsed += dt
        if self.elapsed >= self.duration:
            self.elapsed = self.duration
            self.finished = True
            if self.on_complete:
                self.on_complete()

    def get_progress(self) -> float:
        """获取动画进度 (0.0 - 1.0)"""
        if self.duration <= 0:
            return 1.0
        return min(1.0, self.elapsed / self.duration)

    def get_eased_progress(self) -> float:
        """获取应用缓动函数后的进度"""
        t = self.get_progress()
        return self._apply_easing(t)

    def _apply_easing(self, t: float) -> float:
        """应用缓动函数"""
        if self.easing == 'linear':
            return t
        elif self.easing == 'ease_in':
            return t * t
        elif self.easing == 'ease_out':
            return 1 - (1 - t) * (1 - t)
        elif self.easing == 'ease_in_out':
            if t < 0.5:
                return 2 * t * t
            else:
                return 1 - (-2 * t + 2) ** 2 / 2
        elif self.easing == 'bounce':
            if t < 1 / 2.75:
                return 7.5625 * t * t
            elif t < 2 / 2.75:
                t -= 1.5 / 2.75
                return 7.5625 * t * t + 0.75
            elif t < 2.5 / 2.75:
                t -= 2.25 / 2.75
                return 7.5625 * t * t + 0.9375
            else:
                t -= 2.625 / 2.75
                return 7.5625 * t * t + 0.984375
        return t

    def reset(self):
        """重置动画"""
        self.elapsed = 0.0
        self.finished = False


class FadeAnimation(Animation):
    """淡入淡出动画"""

    def __init__(self, duration: float, start_alpha: int = 0, end_alpha: int = 255,
                 easing: str = 'ease_in_out'):
        super().__init__(duration, easing)
        self.start_alpha = start_alpha
        self.end_alpha = end_alpha

    def get_current_alpha(self) -> int:
        """获取当前透明度"""
        t = self.get_eased_progress()
        return int(self.start_alpha + (self.end_alpha - self.start_alpha) * t)


class MoveAnimation(Animation):
    """移动动画"""

    def __init__(self, duration: float, start_pos: tuple, end_pos: tuple,
                 easing: str = 'ease_out'):
        super().__init__(duration, easing)
        self.start_x, self.start_y = start_pos
        self.end_x, self.end_y = end_pos

    def get_current_pos(self) -> tuple:
        """获取当前位置"""
        t = self.get_eased_progress()
        x = self.start_x + (self.end_x - self.start_x) * t
        y = self.start_y + (self.end_y - self.start_y) * t
        return (int(x), int(y))


class ScaleAnimation(Animation):
    """缩放动画"""

    def __init__(self, duration: float, start_scale: float = 0.5, end_scale: float = 1.0,
                 easing: str = 'ease_out'):
        super().__init__(duration, easing)
        self.start_scale = start_scale
        self.end_scale = end_scale

    def get_current_scale(self) -> float:
        """获取当前缩放比例"""
        t = self.get_eased_progress()
        return self.start_scale + (self.end_scale - self.start_scale) * t


class ColorAnimation(Animation):
    """颜色渐变动画"""

    def __init__(self, duration: float, start_color: tuple, end_color: tuple,
                 easing: str = 'linear'):
        super().__init__(duration, easing)
        self.start_r, self.start_g, self.start_b = start_color[:3]
        self.end_r, self.end_g, self.end_b = end_color[:3]

    def get_current_color(self) -> tuple:
        """获取当前颜色"""
        t = self.get_eased_progress()
        r = int(self.start_r + (self.end_r - self.start_r) * t)
        g = int(self.start_g + (self.end_g - self.start_g) * t)
        b = int(self.start_b + (self.end_b - self.start_b) * t)
        return (r, g, b)


class ShakeAnimation(Animation):
    """抖动动画"""

    def __init__(self, duration: float = 0.5, intensity: float = 5.0):
        super().__init__(duration, 'linear')
        self.intensity = intensity
        self.original_pos = None

    def get_offset(self) -> tuple:
        """获取当前偏移量"""
        if self.finished:
            return (0, 0)

        import random
        progress = self.get_progress()
        # 随时间减弱
        current_intensity = self.intensity * (1 - progress)
        offset_x = random.uniform(-current_intensity, current_intensity)
        offset_y = random.uniform(-current_intensity, current_intensity)
        return (int(offset_x), int(offset_y))


class PulseAnimation(Animation):
    """脉冲动画（循环缩放）"""

    def __init__(self, duration: float = 1.0, min_scale: float = 0.9, max_scale: float = 1.1):
        super().__init__(duration, 'ease_in_out')
        self.min_scale = min_scale
        self.max_scale = max_scale

    def update(self, dt: float):
        """更新动画状态（循环）"""
        self.elapsed += dt
        # 循环动画，不设置finished

    def get_current_scale(self) -> float:
        """获取当前缩放比例（正弦波）"""
        import math
        t = (self.elapsed % self.duration) / self.duration
        # 正弦波 0 -> 1 -> 0
        wave = (math.sin(t * 2 * math.pi) + 1) / 2
        return self.min_scale + (self.max_scale - self.min_scale) * wave


class AnimationManager:
    """动画管理器 - 管理多个动画"""

    def __init__(self):
        self.animations: list[tuple[Any, Animation, str]] = []  # (target, animation, type)

    def add_animation(self, target: Any, animation: Animation, anim_type: str = ''):
        """添加动画

        Args:
            target: 动画目标对象
            animation: 动画实例
            anim_type: 动画类型标识
        """
        self.animations.append((target, animation, anim_type))

    def remove_animation(self, target: Any, anim_type: str = ''):
        """移除动画"""
        self.animations = [
            (t, a, typ) for t, a, typ in self.animations
            if not (t == target and (not anim_type or typ == anim_type))
        ]

    def clear_animations(self):
        """清除所有动画"""
        self.animations.clear()

    def update(self, dt: float):
        """更新所有动画"""
        # 更新动画并移除已完成的
        active_animations = []
        for target, animation, anim_type in self.animations:
            animation.update(dt)
            if not animation.finished or isinstance(animation, PulseAnimation):
                active_animations.append((target, animation, anim_type))
        self.animations = active_animations

    def has_animation(self, target: Any, anim_type: str = '') -> bool:
        """检查是否有特定动画"""
        for t, a, typ in self.animations:
            if t == target and (not anim_type or typ == anim_type):
                return True
        return False


class AnimatedUIComponent:
    """带动画效果的UI组件混入类"""

    def __init__(self):
        self.anim_manager = AnimationManager()
        self._anim_alpha = 255
        self._anim_offset = (0, 0)
        self._anim_scale = 1.0
        self._anim_color = None

    def add_fade_in(self, duration: float = 0.3, delay: float = 0):
        """添加淡入动画"""
        anim = FadeAnimation(duration, 0, 255, 'ease_out')
        anim.elapsed = -delay
        self.anim_manager.add_animation(self, anim, 'fade')

    def add_fade_out(self, duration: float = 0.3, on_complete: Optional[Callable] = None):
        """添加淡出动画"""
        anim = FadeAnimation(duration, 255, 0, 'ease_in')
        anim.on_complete = on_complete
        self.anim_manager.add_animation(self, anim, 'fade')

    def add_slide_in(self, direction: str = 'left', duration: float = 0.4):
        """添加滑入动画

        Args:
            direction: 'left', 'right', 'up', 'down'
        """
        # 需要子类实现获取目标位置
        pass

    def add_scale_in(self, duration: float = 0.3):
        """添加缩放进入动画"""
        anim = ScaleAnimation(duration, 0.5, 1.0, 'ease_out')
        self.anim_manager.add_animation(self, anim, 'scale')

    def add_shake(self, duration: float = 0.5, intensity: float = 5.0):
        """添加抖动动画"""
        anim = ShakeAnimation(duration, intensity)
        self.anim_manager.add_animation(self, anim, 'shake')

    def add_pulse(self, duration: float = 1.0, min_scale: float = 0.95, max_scale: float = 1.05):
        """添加脉冲动画"""
        anim = PulseAnimation(duration, min_scale, max_scale)
        self.anim_manager.add_animation(self, anim, 'pulse')

    def update_animations(self, dt: float):
        """更新动画"""
        self.anim_manager.update(dt)

        # 重置动画属性
        self._anim_alpha = 255
        self._anim_offset = (0, 0)
        self._anim_scale = 1.0
        self._anim_color = None

        # 应用动画效果
        for target, animation, anim_type in self.anim_manager.animations:
            if target is self:
                if isinstance(animation, FadeAnimation):
                    self._anim_alpha = animation.get_current_alpha()
                elif isinstance(animation, MoveAnimation):
                    # 移动动画需要组件支持位置偏移
                    pass
                elif isinstance(animation, ScaleAnimation) or isinstance(animation, PulseAnimation):
                    self._anim_scale = animation.get_current_scale()
                elif isinstance(animation, ShakeAnimation):
                    self._anim_offset = animation.get_offset()
                elif isinstance(animation, ColorAnimation):
                    self._anim_color = animation.get_current_color()

    def get_animation_transform(self) -> dict:
        """获取动画变换参数"""
        return {
            'alpha': self._anim_alpha,
            'offset': self._anim_offset,
            'scale': self._anim_scale,
            'color': self._anim_color
        }


# 全局动画管理器实例
animation_manager = AnimationManager()
