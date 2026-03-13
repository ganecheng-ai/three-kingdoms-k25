"""
三国霸业游戏 - 对话框与提示系统
"""

import pygame
from ui.base import UIComponent, Panel, Button, Label
from utils.constants import COLORS, SCREEN_WIDTH, SCREEN_HEIGHT
from utils.logger import get_logger

logger = get_logger('dialog')


class Dialog(UIComponent):
    """对话框组件"""

    def __init__(self, game, title="", message="", width=400, height=200):
        x = (SCREEN_WIDTH - width) // 2
        y = (SCREEN_HEIGHT - height) // 2
        super().__init__(x, y, width, height)
        self.game = game
        self.title = title
        self.message = message
        self.result = None
        self.callback = None
        self._init_dialog()

    def _init_dialog(self):
        """初始化对话框"""
        # 背景面板
        self.bg_panel = Panel(
            0, 0, self.rect.width, self.rect.height,
            COLORS['panel_bg'], COLORS['border'], 3
        )
        self.add_child(self.bg_panel)

        # 标题
        if self.title:
            self.title_label = Label(
                20, 15, self.title,
                self.game.get_font('large'),
                COLORS['gold']
            )
            self.bg_panel.add_child(self.title_label)

        # 消息文本
        self._update_message()

    def _update_message(self):
        """更新消息显示"""
        # 清除旧的消息标签
        for child in list(self.bg_panel.children):
            if isinstance(child, Label) and child != getattr(self, 'title_label', None):
                self.bg_panel.remove_child(child)

        # 分行显示长文本
        font = self.game.get_font('default')
        words = self.message
        lines = []
        current_line = ""

        for char in words:
            test_line = current_line + char
            if font.size(test_line)[0] > self.rect.width - 60:
                lines.append(current_line)
                current_line = char
            else:
                current_line = test_line

        if current_line:
            lines.append(current_line)

        # 最多显示6行
        lines = lines[:6]

        y_offset = 60 if self.title else 30
        for line in lines:
            line_label = Label(30, y_offset, line, font, COLORS['text'])
            self.bg_panel.add_child(line_label)
            y_offset += 25

    def set_message(self, message):
        """设置消息"""
        self.message = message
        self._update_message()

    def show(self):
        """显示对话框"""
        self.visible = True
        self.enabled = True
        logger.debug(f"显示对话框: {self.title}")

    def hide(self):
        """隐藏对话框"""
        self.visible = False
        self.enabled = False
        logger.debug(f"隐藏对话框: {self.title}")

    def close(self, result=None):
        """关闭对话框"""
        self.result = result
        self.hide()
        if self.callback:
            self.callback(result)


class MessageDialog(Dialog):
    """消息对话框（确定按钮）"""

    def __init__(self, game, title="", message=""):
        super().__init__(game, title, message, 400, 200)
        self._add_ok_button()

    def _add_ok_button(self):
        """添加确定按钮"""
        btn_ok = Button(
            self.rect.width // 2 - 50, self.rect.height - 60,
            100, 35,
            "确定", self.game.get_font('default'),
            COLORS['primary'], COLORS['highlight'], COLORS['white'],
            callback=self._on_ok
        )
        self.bg_panel.add_child(btn_ok)

    def _on_ok(self):
        """确定按钮回调"""
        self.close(True)


class ConfirmDialog(Dialog):
    """确认对话框（确定/取消按钮）"""

    def __init__(self, game, title="", message=""):
        super().__init__(game, title, message, 400, 200)
        self._add_buttons()

    def _add_buttons(self):
        """添加按钮"""
        # 确定按钮
        btn_ok = Button(
            self.rect.width // 2 - 110, self.rect.height - 60,
            100, 35,
            "确定", self.game.get_font('default'),
            COLORS['dark_green'], COLORS['green'], COLORS['white'],
            callback=self._on_ok
        )
        self.bg_panel.add_child(btn_ok)

        # 取消按钮
        btn_cancel = Button(
            self.rect.width // 2 + 10, self.rect.height - 60,
            100, 35,
            "取消", self.game.get_font('default'),
            COLORS['dark_red'], COLORS['red'], COLORS['white'],
            callback=self._on_cancel
        )
        self.bg_panel.add_child(btn_cancel)

    def _on_ok(self):
        """确定按钮回调"""
        self.close(True)

    def _on_cancel(self):
        """取消按钮回调"""
        self.close(False)


class Toast(UIComponent):
    """提示消息（自动消失）"""

    def __init__(self, game, message, duration=2.0, level="info"):
        """
        初始化提示消息
        :param game: 游戏实例
        :param message: 消息内容
        :param duration: 显示时长（秒）
        :param level: 级别 (info, success, warning, error)
        """
        self.game = game
        self.duration = duration
        self.elapsed = 0
        self.level = level

        # 根据级别选择颜色
        color_map = {
            "info": (COLORS['blue'], COLORS['white']),
            "success": (COLORS['green'], COLORS['white']),
            "warning": (COLORS['orange'], COLORS['black']),
            "error": (COLORS['red'], COLORS['white'])
        }
        self.bg_color, self.text_color = color_map.get(level, color_map["info"])

        # 计算尺寸
        font = self.game.get_font('default')
        text_surface = font.render(message, True, self.text_color)
        width = text_surface.get_width() + 40
        height = text_surface.get_height() + 20

        # 居中显示在屏幕上方
        x = (SCREEN_WIDTH - width) // 2
        y = 80

        super().__init__(x, y, width, height)

        self.message = message
        self.alpha = 255

    def update(self, dt):
        """更新"""
        super().update(dt)
        self.elapsed += dt

        # 最后0.5秒淡出
        if self.elapsed > self.duration - 0.5:
            self.alpha = max(0, int(255 * (self.duration - self.elapsed) / 0.5))

        # 时间到自动隐藏
        if self.elapsed >= self.duration:
            self.visible = False
            self.enabled = False

    def _render_self(self, screen):
        """渲染"""
        if not self.visible:
            return

        abs_x, abs_y = self.get_absolute_pos()

        # 创建透明背景
        bg_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        bg_color = (*self.bg_color, self.alpha)
        pygame.draw.rect(bg_surface, bg_color, (0, 0, self.rect.width, self.rect.height), border_radius=5)
        pygame.draw.rect(bg_surface, (*COLORS['white'], self.alpha), (0, 0, self.rect.width, self.rect.height), 2, border_radius=5)

        screen.blit(bg_surface, (abs_x, abs_y))

        # 渲染文字
        font = self.game.get_font('default')
        text_surface = font.render(self.message, True, self.text_color)
        text_surface.set_alpha(self.alpha)
        text_rect = text_surface.get_rect(center=(abs_x + self.rect.width // 2, abs_y + self.rect.height // 2))
        screen.blit(text_surface, text_rect)


class DialogManager:
    """对话框管理器"""

    def __init__(self, game):
        self.game = game
        self.active_dialog = None
        self.toasts = []

    def show_message(self, title, message, callback=None):
        """显示消息对话框"""
        dialog = MessageDialog(self.game, title, message)
        dialog.callback = callback
        dialog.show()
        self.active_dialog = dialog
        logger.info(f"显示消息: {title} - {message}")
        return dialog

    def show_confirm(self, title, message, callback=None):
        """显示确认对话框"""
        dialog = ConfirmDialog(self.game, title, message)
        dialog.callback = callback
        dialog.show()
        self.active_dialog = dialog
        logger.info(f"显示确认: {title} - {message}")
        return dialog

    def show_toast(self, message, duration=2.0, level="info"):
        """显示提示消息"""
        toast = Toast(self.game, message, duration, level)
        self.toasts.append(toast)
        logger.debug(f"显示提示: {message}")
        return toast

    def close_dialog(self):
        """关闭当前对话框"""
        if self.active_dialog:
            self.active_dialog.close()
            self.active_dialog = None

    def handle_event(self, event):
        """处理事件"""
        if self.active_dialog and self.active_dialog.visible:
            return self.active_dialog.handle_event(event)

        # 清理已消失的toast
        self.toasts = [t for t in self.toasts if t.visible]

        return False

    def update(self, dt):
        """更新"""
        if self.active_dialog:
            self.active_dialog.update(dt)

        for toast in self.toasts:
            toast.update(dt)

        # 清理已消失的toast
        self.toasts = [t for t in self.toasts if t.visible]

    def render(self, screen):
        """渲染"""
        # 渲染对话框遮罩层
        if self.active_dialog and self.active_dialog.visible:
            # 半透明黑色背景
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            screen.blit(overlay, (0, 0))
            self.active_dialog.render(screen)

        # 渲染toast
        for toast in self.toasts:
            toast.render(screen)
