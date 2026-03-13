"""
三国霸业游戏 - 战斗场景
"""

import pygame
from scenes.base import BaseScene
from ui.base import Panel, Button, Label
from utils.constants import COLORS, SCREEN_WIDTH, SCREEN_HEIGHT
from utils.logger import get_logger

logger = get_logger('battle')


class BattleScene(BaseScene):
    """战斗场景"""

    def __init__(self, game):
        super().__init__(game)
        self.name = 'battle'

    def _init_scene(self):
        """初始化战斗场景"""
        logger.info("初始化战斗场景")

        # 主面板
        self.ui_root = Panel(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, (50, 80, 50))

        # 顶部信息栏
        self.top_bar = Panel(0, 0, SCREEN_WIDTH, 50, COLORS['dark_gray'])
        self.ui_root.add_child(self.top_bar)

        # 返回按钮
        btn_back = Button(
            20, 10, 60, 30,
            "撤退", self.game.get_font('small'),
            COLORS['dark_red'], COLORS['red'], COLORS['white'],
            callback=self._on_retreat
        )
        self.top_bar.add_child(btn_back)

        # 战斗标题
        self.battle_title = Label(300, 12, "战斗进行中", self.game.get_font('large'), COLORS['gold'])
        self.top_bar.add_child(self.battle_title)

        # 回合数
        self.turn_label = Label(600, 15, "第 1 回合", self.game.get_font('default'), COLORS['white'])
        self.top_bar.add_child(self.turn_label)

        # 战场信息
        self.attacker_label = Label(800, 15, "我军: 10000", self.game.get_font('default'), COLORS['green'])
        self.top_bar.add_child(self.attacker_label)

        self.defender_label = Label(1000, 15, "敌军: 10000", self.game.get_font('default'), COLORS['red'])
        self.top_bar.add_child(self.defender_label)

        # 右侧指令面板
        self.command_panel = Panel(SCREEN_WIDTH - 220, 60, 200, SCREEN_HEIGHT - 80, COLORS['panel_bg'])
        self.ui_root.add_child(self.command_panel)

        self.command_title = Label(20, 20, "战斗指令", self.game.get_font('large'), COLORS['dark_red'])
        self.command_panel.add_child(self.command_title)

        # 指令按钮
        btn_width = 160
        btn_height = 40
        spacing = 50
        start_y = 70

        # 移动
        btn_move = Button(
            20, start_y, btn_width, btn_height,
            "移动", self.game.get_font('default'),
            COLORS['dark_blue'], COLORS['blue'], COLORS['white'],
            callback=self._on_move
        )
        self.command_panel.add_child(btn_move)

        # 攻击
        btn_attack = Button(
            20, start_y + spacing, btn_width, btn_height,
            "攻击", self.game.get_font('default'),
            COLORS['dark_red'], COLORS['red'], COLORS['white'],
            callback=self._on_attack
        )
        self.command_panel.add_child(btn_attack)

        # 计策
        btn_tactic = Button(
            20, start_y + spacing * 2, btn_width, btn_height,
            "计策", self.game.get_font('default'),
            COLORS['purple'], COLORS['gold'], COLORS['white'],
            callback=self._on_tactic
        )
        self.command_panel.add_child(btn_tactic)

        # 阵型
        btn_formation = Button(
            20, start_y + spacing * 3, btn_width, btn_height,
            "阵型", self.game.get_font('default'),
            COLORS['brown'], COLORS['orange'], COLORS['white'],
            callback=self._on_formation
        )
        self.command_panel.add_child(btn_formation)

        # 待机
        btn_wait = Button(
            20, start_y + spacing * 4, btn_width, btn_height,
            "待机", self.game.get_font('default'),
            COLORS['dark_gray'], COLORS['gray'], COLORS['white'],
            callback=self._on_wait
        )
        self.command_panel.add_child(btn_wait)

        # 自动
        btn_auto = Button(
            20, start_y + spacing * 5, btn_width, btn_height,
            "自动", self.game.get_font('default'),
            COLORS['dark_green'], COLORS['green'], COLORS['white'],
            callback=self._on_auto
        )
        self.command_panel.add_child(btn_auto)

        # 回合结束
        btn_end = Button(
            20, start_y + spacing * 7, btn_width, btn_height,
            "回合结束", self.game.get_font('default'),
            COLORS['gold'], (255, 255, 200), COLORS['dark_red'],
            callback=self._on_end_turn
        )
        self.command_panel.add_child(btn_end)

        # 战场区域
        self.battlefield = pygame.Rect(20, 60, SCREEN_WIDTH - 260, SCREEN_HEIGHT - 80)

        # 示例单位数据
        self.units = [
            {'x': 100, 'y': 200, 'faction': 'player', 'name': '刘备'},
            {'x': 150, 'y': 250, 'faction': 'player', 'name': '关羽'},
            {'x': 200, 'y': 300, 'faction': 'player', 'name': '张飞'},
            {'x': 600, 'y': 200, 'faction': 'enemy', 'name': '曹操'},
            {'x': 650, 'y': 250, 'faction': 'enemy', 'name': '夏侯惇'},
            {'x': 700, 'y': 300, 'faction': 'enemy', 'name': '张辽'},
        ]

    def _on_retreat(self):
        """撤退"""
        logger.info("撤退")
        self.game.change_scene('world_map')

    def _on_move(self):
        """移动"""
        logger.info("移动指令")

    def _on_attack(self):
        """攻击"""
        logger.info("攻击指令")

    def _on_tactic(self):
        """计策"""
        logger.info("计策指令")

    def _on_formation(self):
        """阵型"""
        logger.info("阵型指令")

    def _on_wait(self):
        """待机"""
        logger.info("待机指令")

    def _on_auto(self):
        """自动战斗"""
        logger.info("自动战斗")

    def _on_end_turn(self):
        """回合结束"""
        logger.info("战斗回合结束")

    def handle_event(self, event):
        """处理事件"""
        self.ui_root.handle_event(event)

    def update(self, dt):
        """更新"""
        self.ui_root.update(dt)

    def render(self, screen):
        """渲染"""
        self.ui_root.render(screen)

        # 渲染战场
        self._render_battlefield(screen)

        # 渲染单位
        self._render_units(screen)

    def _render_battlefield(self, screen):
        """渲染战场背景"""
        # 战场背景
        pygame.draw.rect(screen, (100, 150, 100), self.battlefield)

        # 绘制网格
        grid_size = 50
        for x in range(self.battlefield.left, self.battlefield.right, grid_size):
            pygame.draw.line(screen, (80, 120, 80), (x, self.battlefield.top), (x, self.battlefield.bottom))
        for y in range(self.battlefield.top, self.battlefield.bottom, grid_size):
            pygame.draw.line(screen, (80, 120, 80), (self.battlefield.left, y), (self.battlefield.right, y))

    def _render_units(self, screen):
        """渲染战斗单位"""
        for unit in self.units:
            x = self.battlefield.left + unit['x']
            y = self.battlefield.top + unit['y']

            # 根据势力选择颜色
            if unit['faction'] == 'player':
                color = COLORS['green']
            else:
                color = COLORS['red']

            # 绘制单位（圆形）
            pygame.draw.circle(screen, color, (x, y), 20)
            pygame.draw.circle(screen, COLORS['black'], (x, y), 20, 2)

            # 单位名称
            name_surface = self.game.get_font('small').render(unit['name'], True, COLORS['white'])
            name_rect = name_surface.get_rect(center=(x, y))
            screen.blit(name_surface, name_rect)
