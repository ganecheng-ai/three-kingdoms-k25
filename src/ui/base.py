"""
三国霸业游戏 - UI基础组件
"""

import pygame
from utils.constants import COLORS
from utils.logger import get_logger

logger = get_logger('ui')


class UIComponent:
    """UI组件基类"""

    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.visible = True
        self.enabled = True
        self.parent = None
        self.children = []

    def add_child(self, child):
        """添加子组件"""
        child.parent = self
        self.children.append(child)

    def remove_child(self, child):
        """移除子组件"""
        if child in self.children:
            child.parent = None
            self.children.remove(child)

    def handle_event(self, event):
        """处理事件"""
        if not self.visible or not self.enabled:
            return False

        # 传递给子组件
        for child in self.children:
            if child.handle_event(event):
                return True

        return False

    def update(self, dt):
        """更新组件"""
        if not self.visible:
            return

        for child in self.children:
            child.update(dt)

    def render(self, screen):
        """渲染组件"""
        if not self.visible:
            return

        self._render_self(screen)

        for child in self.children:
            child.render(screen)

    def _render_self(self, screen):
        """渲染自身（子类重写）"""
        pass

    def get_absolute_pos(self):
        """获取绝对位置"""
        x, y = self.rect.x, self.rect.y
        if self.parent:
            px, py = self.parent.get_absolute_pos()
            x += px
            y += py
        return (x, y)


class Panel(UIComponent):
    """面板组件"""

    def __init__(self, x, y, width, height, bg_color=None, border_color=None, border_width=2):
        super().__init__(x, y, width, height)
        self.bg_color = bg_color or COLORS['panel_bg']
        self.border_color = border_color or COLORS['border']
        self.border_width = border_width

    def _render_self(self, screen):
        """渲染面板"""
        abs_x, abs_y = self.get_absolute_pos()

        # 绘制背景
        pygame.draw.rect(screen, self.bg_color, (abs_x, abs_y, self.rect.width, self.rect.height))

        # 绘制边框
        if self.border_width > 0:
            pygame.draw.rect(screen, self.border_color, (abs_x, abs_y, self.rect.width, self.rect.height), self.border_width)


class Label(UIComponent):
    """文本标签组件"""

    def __init__(self, x, y, text, font=None, color=None, bg_color=None):
        super().__init__(x, y, 0, 0)
        self.text = text
        self.font = font
        self.color = color or COLORS['text']
        self.bg_color = bg_color
        self._update_rect()

    def set_text(self, text):
        """设置文本"""
        self.text = text
        self._update_rect()

    def _update_rect(self):
        """更新尺寸"""
        if self.font:
            surface = self.font.render(self.text, True, self.color)
            self.rect.width = surface.get_width()
            self.rect.height = surface.get_height()

    def _render_self(self, screen):
        """渲染文本"""
        if not self.font:
            return

        abs_x, abs_y = self.get_absolute_pos()
        surface = self.font.render(self.text, True, self.color)

        if self.bg_color:
            bg_rect = surface.get_rect(x=abs_x, y=abs_y)
            pygame.draw.rect(screen, self.bg_color, bg_rect)

        screen.blit(surface, (abs_x, abs_y))


class Button(UIComponent):
    """按钮组件"""

    def __init__(self, x, y, width, height, text, font=None,
                 bg_color=None, hover_color=None, text_color=None,
                 border_color=None, callback=None):
        super().__init__(x, y, width, height)
        self.text = text
        self.font = font
        self.bg_color = bg_color or COLORS['primary']
        self.hover_color = hover_color or COLORS['highlight']
        self.text_color = text_color or COLORS['text_light']
        self.border_color = border_color or COLORS['border']
        self.callback = callback
        self.hovered = False
        self.pressed = False

    def handle_event(self, event):
        """处理事件"""
        if not self.visible or not self.enabled:
            return False

        abs_x, abs_y = self.get_absolute_pos()
        mouse_pos = pygame.mouse.get_pos()
        in_bounds = (abs_x <= mouse_pos[0] <= abs_x + self.rect.width and
                     abs_y <= mouse_pos[1] <= abs_y + self.rect.height)

        if event.type == pygame.MOUSEMOTION:
            self.hovered = in_bounds

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and in_bounds:
                self.pressed = True
                return True

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if self.pressed and in_bounds and self.callback:
                    self.callback()
                self.pressed = False

        return False

    def _render_self(self, screen):
        """渲染按钮"""
        abs_x, abs_y = self.get_absolute_pos()

        # 选择颜色
        if self.pressed:
            color = self.hover_color
        elif self.hovered:
            color = self.hover_color
        else:
            color = self.bg_color

        # 绘制按钮背景
        pygame.draw.rect(screen, color, (abs_x, abs_y, self.rect.width, self.rect.height))

        # 绘制边框
        pygame.draw.rect(screen, self.border_color, (abs_x, abs_y, self.rect.width, self.rect.height), 2)

        # 绘制文字
        if self.font:
            text_surface = self.font.render(self.text, True, self.text_color)
            text_rect = text_surface.get_rect(
                center=(abs_x + self.rect.width // 2, abs_y + self.rect.height // 2)
            )
            screen.blit(text_surface, text_rect)


class ScrollPanel(Panel):
    """可滚动面板组件"""

    def __init__(self, x, y, width, height, bg_color=None, border_color=None, border_width=2):
        super().__init__(x, y, width, height, bg_color, border_color, border_width)
        self.scroll_y = 0
        self.max_scroll = 0
        self.content_height = 0
        self.scrollbar_width = 10
        self.scrollbar_color = (100, 100, 100)
        self.scrollbar_bg_color = (60, 60, 60)
        self.dragging_scrollbar = False
        self.drag_start_y = 0
        self.drag_start_scroll = 0

    def add_child(self, child):
        """添加子组件并更新内容高度"""
        super().add_child(child)
        self._update_content_height()

    def remove_child(self, child):
        """移除子组件并更新内容高度"""
        super().remove_child(child)
        self._update_content_height()

    def _update_content_height(self):
        """更新内容高度"""
        if not self.children:
            self.content_height = 0
            self.max_scroll = 0
            return

        max_y = 0
        for child in self.children:
            child_bottom = child.rect.y + child.rect.height
            if child_bottom > max_y:
                max_y = child_bottom

        self.content_height = max_y
        self.max_scroll = max(0, self.content_height - self.rect.height + 10)

    def handle_event(self, event):
        """处理事件"""
        if not self.visible or not self.enabled:
            return False

        # 处理滚动条拖拽
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                abs_x, abs_y = self.get_absolute_pos()
                scrollbar_x = abs_x + self.rect.width - self.scrollbar_width - 2
                scrollbar_y = abs_y + 2
                scrollbar_height = self.rect.height - 4

                mouse_pos = pygame.mouse.get_pos()
                if (scrollbar_x <= mouse_pos[0] <= scrollbar_x + self.scrollbar_width and
                    scrollbar_y <= mouse_pos[1] <= scrollbar_y + scrollbar_height):
                    self.dragging_scrollbar = True
                    self.drag_start_y = mouse_pos[1]
                    self.drag_start_scroll = self.scroll_y
                    return True

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging_scrollbar = False

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging_scrollbar:
                delta_y = event.pos[1] - self.drag_start_y
                scroll_range = self.max_scroll if self.max_scroll > 0 else 1
                scroll_ratio = delta_y / (self.rect.height - 20)
                self.scroll_y = self.drag_start_scroll + int(scroll_ratio * scroll_range)
                self.scroll_y = max(0, min(self.scroll_y, self.max_scroll))
                return True

        # 处理滚轮
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # 滚轮上
                self.scroll_y = max(0, self.scroll_y - 30)
                return True
            elif event.button == 5:  # 滚轮下
                self.scroll_y = min(self.max_scroll, self.scroll_y + 30)
                return True

        # 传递给子组件（考虑滚动偏移）
        for child in self.children:
            if child.handle_event(event):
                return True

        return False

    def _render_self(self, screen):
        """渲染面板"""
        abs_x, abs_y = self.get_absolute_pos()

        # 绘制背景
        pygame.draw.rect(screen, self.bg_color, (abs_x, abs_y, self.rect.width, self.rect.height))

        # 绘制边框
        if self.border_width > 0:
            pygame.draw.rect(screen, self.border_color,
                           (abs_x, abs_y, self.rect.width, self.rect.height), self.border_width)

        # 绘制滚动条背景
        scrollbar_x = abs_x + self.rect.width - self.scrollbar_width - 2
        pygame.draw.rect(screen, self.scrollbar_bg_color,
                       (scrollbar_x, abs_y + 2, self.scrollbar_width, self.rect.height - 4))

        # 绘制滚动条滑块
        if self.max_scroll > 0:
            thumb_height = max(30, int((self.rect.height - 20) * self.rect.height / self.content_height))
            thumb_y = abs_y + 2 + int((self.rect.height - 4 - thumb_height) * self.scroll_y / self.max_scroll)
            pygame.draw.rect(screen, self.scrollbar_color,
                           (scrollbar_x, thumb_y, self.scrollbar_width, thumb_height))

    def render(self, screen):
        """渲染组件"""
        if not self.visible:
            return

        self._render_self(screen)

        # 创建裁剪区域
        abs_x, abs_y = self.get_absolute_pos()
        old_clip = screen.get_clip()
        clip_rect = pygame.Rect(abs_x + 1, abs_y + 1, self.rect.width - 2 - self.scrollbar_width, self.rect.height - 2)
        screen.set_clip(clip_rect)

        # 渲染子组件（考虑滚动偏移）
        for child in self.children:
            if isinstance(child, Label) or isinstance(child, Button):
                # 临时调整位置以应用滚动
                original_y = child.rect.y
                child.rect.y = original_y - self.scroll_y
                child.render(screen)
                child.rect.y = original_y
            else:
                child.render(screen)

        # 恢复裁剪区域
        screen.set_clip(old_clip)
