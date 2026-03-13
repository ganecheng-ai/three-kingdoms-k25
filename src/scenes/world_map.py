"""
三国霸业游戏 - 大地图场景
"""

import pygame
from scenes.base import BaseScene
from ui.base import Panel, Button, Label
from utils.constants import COLORS, SCREEN_WIDTH, SCREEN_HEIGHT, TERRAIN_COLORS, FACTION_COLORS
from utils.logger import get_logger
from core.city import city_manager
from core.faction import faction_manager

logger = get_logger('world_map')


class WorldMapScene(BaseScene):
    """大地图场景"""

    def __init__(self, game):
        super().__init__(game)
        self.name = 'world_map'
        self.map_offset_x = 0
        self.map_offset_y = 0
        self.map_width = 1400
        self.map_height = 1000

    def _init_scene(self):
        """初始化大地图"""
        logger.info("初始化大地图")

        # 主UI面板
        self.ui_root = Panel(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, COLORS['background'])

        # 顶部信息栏
        self.top_bar = Panel(0, 0, SCREEN_WIDTH, 60, COLORS['primary'])
        self.ui_root.add_child(self.top_bar)

        # 势力名称
        self.faction_name_label = Label(20, 15, "势力名称", self.game.get_font('large'), COLORS['gold'])
        self.top_bar.add_child(self.faction_name_label)

        # 日期显示
        self.date_label = Label(300, 15, "公元 184年 1月", self.game.get_font('large'), COLORS['white'])
        self.top_bar.add_child(self.date_label)

        # 回合数
        self.turn_label = Label(550, 15, "第 1 回合", self.game.get_font('default'), COLORS['light_gray'])
        self.top_bar.add_child(self.turn_label)

        # 资源显示
        self.gold_label = Label(700, 15, "金钱: 0", self.game.get_font('default'), COLORS['gold'])
        self.top_bar.add_child(self.gold_label)

        self.food_label = Label(850, 15, "粮草: 0", self.game.get_font('default'), COLORS['light_gray'])
        self.top_bar.add_child(self.food_label)

        self.troops_label = Label(1000, 15, "兵力: 0", self.game.get_font('default'), COLORS['red'])
        self.top_bar.add_child(self.troops_label)

        # 底部菜单栏
        self.bottom_bar = Panel(0, SCREEN_HEIGHT - 80, SCREEN_WIDTH, 80, COLORS['primary'])
        self.ui_root.add_child(self.bottom_bar)

        # 菜单按钮
        btn_width = 100
        btn_height = 40
        btn_y = 20
        spacing = 120
        start_x = 50

        # 内政按钮
        btn_internal = Button(
            start_x, btn_y, btn_width, btn_height,
            "内政", self.game.get_font('default'),
            COLORS['dark_green'], COLORS['green'], COLORS['white'],
            callback=self._on_internal
        )
        self.bottom_bar.add_child(btn_internal)

        # 军事按钮
        btn_military = Button(
            start_x + spacing, btn_y, btn_width, btn_height,
            "军事", self.game.get_font('default'),
            COLORS['dark_red'], COLORS['red'], COLORS['white'],
            callback=self._on_military
        )
        self.bottom_bar.add_child(btn_military)

        # 外交按钮
        btn_diplomacy = Button(
            start_x + spacing * 2, btn_y, btn_width, btn_height,
            "外交", self.game.get_font('default'),
            COLORS['dark_blue'], COLORS['blue'], COLORS['white'],
            callback=self._on_diplomacy
        )
        self.bottom_bar.add_child(btn_diplomacy)

        # 人事按钮
        btn_personnel = Button(
            start_x + spacing * 3, btn_y, btn_width, btn_height,
            "人事", self.game.get_font('default'),
            COLORS['brown'], COLORS['orange'], COLORS['white'],
            callback=self._on_personnel
        )
        self.bottom_bar.add_child(btn_personnel)

        # 情报按钮
        btn_intel = Button(
            start_x + spacing * 4, btn_y, btn_width, btn_height,
            "情报", self.game.get_font('default'),
            COLORS['purple'], COLORS['gold'], COLORS['white'],
            callback=self._on_intel
        )
        self.bottom_bar.add_child(btn_intel)

        # 系统按钮
        btn_system = Button(
            start_x + spacing * 8, btn_y, btn_width, btn_height,
            "系统", self.game.get_font('default'),
            COLORS['dark_gray'], COLORS['gray'], COLORS['white'],
            callback=self._on_system
        )
        self.bottom_bar.add_child(btn_system)

        # 回合结束按钮
        btn_end_turn = Button(
            SCREEN_WIDTH - 150, btn_y, 120, btn_height,
            "结束回合", self.game.get_font('default'),
            COLORS['gold'], (255, 255, 200), COLORS['dark_red'],
            callback=self._on_end_turn
        )
        self.bottom_bar.add_child(btn_end_turn)

        # 地图视口
        self.map_viewport = pygame.Rect(0, 60, SCREEN_WIDTH, SCREEN_HEIGHT - 140)

        # 生成地形
        self._generate_terrain()

        # 更新显示
        self._update_display()

    def on_enter(self, *args, **kwargs):
        """进入场景"""
        super().on_enter(*args, **kwargs)
        self._update_display()

    def _update_display(self):
        """更新显示信息"""
        # 更新势力名称
        player_faction = self.game.get_player_faction()
        if player_faction:
            self.faction_name_label.set_text(f"{player_faction.name}军")
            self.faction_name_label.color = player_faction.color

        # 更新日期
        self.date_label.set_text(self.game.get_formatted_date())

        # 更新回合
        self.turn_label.set_text(f"第 {self.game.current_turn} 回合")

        # 更新资源
        if player_faction:
            player_faction.update_resources(self.game.city_manager.cities)
            self.gold_label.set_text(f"金钱: {player_faction.total_gold}")
            self.food_label.set_text(f"粮草: {player_faction.total_food}")
            self.troops_label.set_text(f"兵力: {player_faction.total_troops}")

    def _generate_terrain(self):
        """生成地形数据"""
        import random
        random.seed(42)

        self.terrain = []
        tile_size = 40

        for y in range(0, self.map_height, tile_size):
            row = []
            for x in range(0, self.map_width, tile_size):
                # 简化地形生成
                noise = random.random()
                if noise < 0.1:
                    terrain_type = 'water'
                elif noise < 0.3:
                    terrain_type = 'mountain'
                elif noise < 0.5:
                    terrain_type = 'forest'
                else:
                    terrain_type = 'plain'
                row.append(terrain_type)
            self.terrain.append(row)

    def _on_internal(self):
        """内政"""
        logger.info("打开内政界面")
        # 如果有选中的城池，直接进入该城
        if self.game.selected_city:
            self.game.change_scene('city', self.game.selected_city)
        else:
            # 获取玩家第一个城池
            player_cities = self.game.get_player_cities()
            if player_cities:
                self.game.change_scene('city', player_cities[0])

    def _on_military(self):
        """军事"""
        logger.info("打开军事界面")

    def _on_diplomacy(self):
        """外交"""
        logger.info("打开外交界面")

    def _on_personnel(self):
        """人事"""
        logger.info("打开人事界面")

    def _on_intel(self):
        """情报"""
        logger.info("打开情报界面")

    def _on_system(self):
        """系统"""
        logger.info("打开系统菜单")

    def _on_end_turn(self):
        """结束回合"""
        logger.info("结束回合")
        self.game.next_turn()
        self._update_display()

    def handle_event(self, event):
        """处理事件"""
        self.ui_root.handle_event(event)

        if event.type == pygame.MOUSEMOTION:
            # 地图拖动
            if event.buttons[0]:
                self.map_offset_x += event.rel[0]
                self.map_offset_y += event.rel[1]
                self._clamp_map_offset()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                # 检查是否点击了城池
                mouse_x, mouse_y = event.pos
                self._check_city_click(mouse_x, mouse_y)

    def _clamp_map_offset(self):
        """限制地图偏移范围"""
        self.map_offset_x = max(-(self.map_width - self.map_viewport.width), min(0, self.map_offset_x))
        self.map_offset_y = max(-(self.map_height - self.map_viewport.height), min(0, self.map_offset_y))

    def _check_city_click(self, mouse_x, mouse_y):
        """检查是否点击了城池"""
        for city in city_manager.cities.values():
            city_screen_x = city.x + self.map_offset_x
            city_screen_y = city.y + self.map_offset_y + self.map_viewport.y

            # 检查点击范围（城池半径约20像素）
            dx = mouse_x - city_screen_x
            dy = mouse_y - city_screen_y
            if dx * dx + dy * dy <= 400:  # 20^2 = 400
                logger.info(f"点击城池: {city.name}")
                self.game.select_city(city.id)
                self.game.change_scene('city', city)
                break

    def update(self, dt):
        """更新"""
        self.ui_root.update(dt)

    def render(self, screen):
        """渲染"""
        self.ui_root.render(screen)

        # 渲染地图区域
        self._render_map(screen)

    def _render_map(self, screen):
        """渲染地图"""
        clip_rect = screen.get_clip()
        screen.set_clip(self.map_viewport)

        # 渲染地形
        tile_size = 40
        start_row = max(0, -self.map_offset_y // tile_size)
        end_row = min(len(self.terrain), start_row + self.map_viewport.height // tile_size + 2)

        for row_idx in range(start_row, end_row):
            if row_idx < len(self.terrain):
                row = self.terrain[row_idx]
                start_col = max(0, -self.map_offset_x // tile_size)
                end_col = min(len(row), start_col + self.map_viewport.width // tile_size + 2)

                for col_idx in range(start_col, end_col):
                    if col_idx < len(row):
                        terrain_type = row[col_idx]
                        x = col_idx * tile_size + self.map_offset_x
                        y = row_idx * tile_size + self.map_offset_y + self.map_viewport.y

                        if terrain_type in TERRAIN_COLORS:
                            color = TERRAIN_COLORS[terrain_type]
                            pygame.draw.rect(screen, color, (x, y, tile_size, tile_size))

        # 渲染城池
        for city in city_manager.cities.values():
            x = city.x + self.map_offset_x
            y = city.y + self.map_offset_y + self.map_viewport.y

            # 城池圆圈
            color = FACTION_COLORS.get(city.faction_id, (128, 128, 128))

            # 如果选中则高亮
            if self.game.selected_city and self.game.selected_city.id == city.id:
                pygame.draw.circle(screen, COLORS['yellow'], (int(x), int(y)), 20)

            pygame.draw.circle(screen, color, (int(x), int(y)), 15)
            pygame.draw.circle(screen, COLORS['black'], (int(x), int(y)), 15, 2)

            # 城池名称
            name_surface = self.game.get_font('small').render(city.name, True, COLORS['white'])
            name_rect = name_surface.get_rect(center=(int(x), int(y) + 25))

            # 名称背景
            bg_rect = name_rect.inflate(4, 2)
            pygame.draw.rect(screen, COLORS['black'], bg_rect)
            screen.blit(name_surface, name_rect)

            # 显示兵力
            if city.troops > 0:
                troop_text = f"{city.troops // 1000}k"
                troop_surface = self.game.get_font('small').render(troop_text, True, COLORS['white'])
                troop_rect = troop_surface.get_rect(center=(int(x), int(y)))
                screen.blit(troop_surface, troop_rect)

        screen.set_clip(clip_rect)
