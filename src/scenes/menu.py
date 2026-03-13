"""
三国霸业游戏 - 主菜单场景
"""

import pygame
from scenes.base import BaseScene
from ui.base import Panel, Button, Label
from utils.constants import COLORS, SCREEN_WIDTH, SCREEN_HEIGHT
from utils.logger import get_logger

logger = get_logger('menu')


class MenuScene(BaseScene):
    """主菜单场景"""

    def __init__(self, game):
        super().__init__(game)
        self.name = 'menu'

    def _init_scene(self):
        """初始化主菜单"""
        logger.info("初始化主菜单")

        self.ui_root = Panel(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, COLORS['background'])

        # 标题
        title = Label(
            SCREEN_WIDTH // 2 - 150, 80,
            "三国霸业",
            self.game.get_font('title'),
            COLORS['dark_red']
        )
        self.ui_root.add_child(title)

        # 副标题
        subtitle = Label(
            SCREEN_WIDTH // 2 - 100, 140,
            "策略争霸，一统天下",
            self.game.get_font('default'),
            COLORS['text']
        )
        self.ui_root.add_child(subtitle)

        # 按钮区域
        button_width = 200
        button_height = 50
        button_x = SCREEN_WIDTH // 2 - button_width // 2
        start_y = 250
        spacing = 70

        # 新游戏按钮
        btn_new_game = Button(
            button_x, start_y,
            button_width, button_height,
            "新游戏",
            self.game.get_font('large'),
            COLORS['primary'],
            COLORS['highlight'],
            COLORS['text_light'],
            callback=self._on_new_game
        )
        self.ui_root.add_child(btn_new_game)

        # 载入游戏按钮
        btn_load_game = Button(
            button_x, start_y + spacing,
            button_width, button_height,
            "载入游戏",
            self.game.get_font('large'),
            COLORS['primary'],
            COLORS['highlight'],
            COLORS['text_light'],
            callback=self._on_load_game
        )
        self.ui_root.add_child(btn_load_game)

        # 游戏设置按钮
        btn_settings = Button(
            button_x, start_y + spacing * 2,
            button_width, button_height,
            "游戏设置",
            self.game.get_font('large'),
            COLORS['primary'],
            COLORS['highlight'],
            COLORS['text_light'],
            callback=self._on_settings
        )
        self.ui_root.add_child(btn_settings)

        # 退出游戏按钮
        btn_exit = Button(
            button_x, start_y + spacing * 3,
            button_width, button_height,
            "退出游戏",
            self.game.get_font('large'),
            COLORS['dark_red'],
            COLORS['red'],
            COLORS['text_light'],
            callback=self._on_exit
        )
        self.ui_root.add_child(btn_exit)

        # 版本信息
        version = Label(
            SCREEN_WIDTH - 150, SCREEN_HEIGHT - 30,
            "版本 v0.1.0",
            self.game.get_font('small'),
            COLORS['gray']
        )
        self.ui_root.add_child(version)

    def _on_new_game(self):
        """新游戏"""
        logger.info("开始新游戏")
        self.game.change_scene('world_map')

    def _on_load_game(self):
        """载入游戏"""
        logger.info("载入游戏")
        # TODO: 实现存档列表
        pass

    def _on_settings(self):
        """游戏设置"""
        logger.info("打开设置")
        # TODO: 实现设置界面
        pass

    def _on_exit(self):
        """退出游戏"""
        logger.info("退出游戏")
        self.game.running = False

    def handle_event(self, event):
        """处理事件"""
        self.ui_root.handle_event(event)

    def update(self, dt):
        """更新"""
        self.ui_root.update(dt)

    def render(self, screen):
        """渲染"""
        self.ui_root.render(screen)
