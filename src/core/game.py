"""
三国霸业游戏 - 游戏主控制
"""

import pygame
import sys
import os

from config import config
from utils.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS,
    GAME_STATE_MENU, GAME_STATE_PLAYING, GAME_STATE_PAUSED
)
from utils.logger import get_logger
from scenes.menu import MenuScene
from scenes.world_map import WorldMapScene
from scenes.city import CityScene
from scenes.battle import BattleScene

logger = get_logger('game')


class Game:
    """游戏主类"""

    def __init__(self):
        """初始化游戏"""
        logger.info("初始化游戏...")

        # 初始化 Pygame
        pygame.init()
        pygame.display.set_caption("三国霸业")

        # 创建窗口
        self.screen_size = config.get_display_size()
        self.screen = pygame.display.set_mode(self.screen_size)
        self.clock = pygame.time.Clock()
        self.running = False
        self.state = GAME_STATE_MENU

        # 字体（先使用系统字体）
        self.fonts = {}
        self._init_fonts()

        # 场景管理
        self.scenes = {}
        self.current_scene = None
        self._init_scenes()

        logger.info("游戏初始化完成")

    def _init_fonts(self):
        """初始化字体"""
        try:
            # 尝试加载中文字体
            font_paths = [
                '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',  # Linux
                '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
                '/System/Library/Fonts/PingFang.ttc',  # macOS
                'C:/Windows/Fonts/simhei.ttf',  # Windows
                'C:/Windows/Fonts/msyh.ttc',
            ]

            chinese_font = None
            for path in font_paths:
                if os.path.exists(path):
                    chinese_font = path
                    break

            if chinese_font:
                self.fonts['default'] = pygame.font.Font(chinese_font, 16)
                self.fonts['title'] = pygame.font.Font(chinese_font, 36)
                self.fonts['large'] = pygame.font.Font(chinese_font, 24)
                self.fonts['small'] = pygame.font.Font(chinese_font, 12)
                logger.info(f"使用中文字体: {chinese_font}")
            else:
                # 使用系统默认字体
                self.fonts['default'] = pygame.font.SysFont('simhei', 16)
                self.fonts['title'] = pygame.font.SysFont('simhei', 36)
                self.fonts['large'] = pygame.font.SysFont('simhei', 24)
                self.fonts['small'] = pygame.font.SysFont('simhei', 12)
                logger.info("使用系统默认字体")

        except Exception as e:
            logger.error(f"字体初始化失败: {e}")
            # 使用pygame默认字体
            self.fonts['default'] = pygame.font.Font(None, 16)
            self.fonts['title'] = pygame.font.Font(None, 36)
            self.fonts['large'] = pygame.font.Font(None, 24)
            self.fonts['small'] = pygame.font.Font(None, 12)

    def _init_scenes(self):
        """初始化场景"""
        self.scenes['menu'] = MenuScene(self)
        self.scenes['world_map'] = WorldMapScene(self)
        self.scenes['city'] = CityScene(self)
        self.scenes['battle'] = BattleScene(self)

        # 设置初始场景
        self.change_scene('menu')

    def change_scene(self, scene_name, *args, **kwargs):
        """切换场景"""
        if scene_name in self.scenes:
            if self.current_scene:
                self.current_scene.on_exit()

            logger.info(f"切换场景: {scene_name}")
            self.current_scene = self.scenes[scene_name]
            self.current_scene.on_enter(*args, **kwargs)
        else:
            logger.error(f"场景不存在: {scene_name}")

    def get_font(self, name='default'):
        """获取字体"""
        return self.fonts.get(name, self.fonts['default'])

    def run(self):
        """运行游戏主循环"""
        self.running = True
        logger.info("游戏主循环开始")

        while self.running:
            dt = self.clock.tick(FPS) / 1000.0  # 获取帧时间（秒）

            # 处理事件
            self._handle_events()

            # 更新
            self._update(dt)

            # 渲染
            self._render()

            # 更新显示
            pygame.display.flip()

        self.quit()

    def _handle_events(self):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                logger.info("收到退出事件")
            else:
                # 传递给当前场景
                if self.current_scene:
                    self.current_scene.handle_event(event)

    def _update(self, dt):
        """更新游戏状态"""
        if self.current_scene:
            self.current_scene.update(dt)

    def _render(self):
        """渲染游戏画面"""
        # 清屏
        self.screen.fill((0, 0, 0))

        # 渲染当前场景
        if self.current_scene:
            self.current_scene.render(self.screen)

        # 显示FPS（调试模式）
        if config.get('debug.show_fps'):
            fps_text = self.get_font('small').render(f"FPS: {int(self.clock.get_fps())}", True, (255, 255, 0))
            self.screen.blit(fps_text, (10, 10))

    def quit(self):
        """退出游戏"""
        logger.info("游戏退出中...")

        # 通知所有场景退出
        for scene in self.scenes.values():
            scene.on_exit()

        pygame.quit()
        sys.exit(0)
