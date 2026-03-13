"""
三国霸业游戏 - 城市管理场景
"""

import pygame
from scenes.base import BaseScene
from ui.base import Panel, Button, Label
from utils.constants import COLORS, SCREEN_WIDTH, SCREEN_HEIGHT
from utils.logger import get_logger

logger = get_logger('city')


class CityScene(BaseScene):
    """城市界面场景"""

    def __init__(self, game):
        super().__init__(game)
        self.name = 'city'
        self.current_city = None

    def _init_scene(self):
        """初始化城市界面"""
        logger.info("初始化城市界面")

        # 主面板
        self.ui_root = Panel(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, COLORS['background'])

        # 顶部信息栏
        self.top_bar = Panel(0, 0, SCREEN_WIDTH, 60, COLORS['primary'])
        self.ui_root.add_child(self.top_bar)

        # 返回按钮
        btn_back = Button(
            20, 15, 80, 30,
            "返回", self.game.get_font('default'),
            COLORS['dark_gray'], COLORS['gray'], COLORS['white'],
            callback=self._on_back
        )
        self.top_bar.add_child(btn_back)

        # 城池名称
        self.city_name = Label(300, 15, "城池名称", self.game.get_font('large'), COLORS['gold'])
        self.top_bar.add_child(self.city_name)

        # 左侧信息面板
        self.left_panel = Panel(20, 80, 300, SCREEN_HEIGHT - 160, COLORS['panel_bg'])
        self.ui_root.add_child(self.left_panel)

        # 城池信息标题
        self.info_title = Label(20, 20, "城池信息", self.game.get_font('large'), COLORS['dark_red'])
        self.left_panel.add_child(self.info_title)

        # 城池属性
        self.population_label = Label(20, 60, "人口: 0", self.game.get_font('default'), COLORS['text'])
        self.left_panel.add_child(self.population_label)

        self.agriculture_label = Label(20, 90, "农业: 0", self.game.get_font('default'), COLORS['text'])
        self.left_panel.add_child(self.agriculture_label)

        self.commerce_label = Label(20, 120, "商业: 0", self.game.get_font('default'), COLORS['text'])
        self.left_panel.add_child(self.commerce_label)

        self.defense_label = Label(20, 150, "城防: 0", self.game.get_font('default'), COLORS['text'])
        self.left_panel.add_child(self.defense_label)

        self.gold_label = Label(20, 180, "金钱: 0", self.game.get_font('default'), COLORS['text'])
        self.left_panel.add_child(self.gold_label)

        self.food_label = Label(20, 210, "粮草: 0", self.game.get_font('default'), COLORS['text'])
        self.left_panel.add_child(self.food_label)

        self.troops_label = Label(20, 240, "兵力: 0", self.game.get_font('default'), COLORS['text'])
        self.left_panel.add_child(self.troops_label)

        # 中间武将列表
        self.middle_panel = Panel(340, 80, 400, SCREEN_HEIGHT - 160, COLORS['panel_bg'])
        self.ui_root.add_child(self.middle_panel)

        self.officers_title = Label(20, 20, "城中武将", self.game.get_font('large'), COLORS['dark_red'])
        self.middle_panel.add_child(self.officers_title)

        # 右侧操作面板
        self.right_panel = Panel(760, 80, 500, SCREEN_HEIGHT - 160, COLORS['panel_bg'])
        self.ui_root.add_child(self.right_panel)

        self.action_title = Label(20, 20, "内政操作", self.game.get_font('large'), COLORS['dark_red'])
        self.right_panel.add_child(self.action_title)

        # 操作按钮
        btn_width = 120
        btn_height = 40
        spacing = 60

        # 开发农业
        btn_agri = Button(
            20, 70, btn_width, btn_height,
            "开发农业", self.game.get_font('default'),
            COLORS['dark_green'], COLORS['green'], COLORS['white'],
            callback=self._on_develop_agriculture
        )
        self.right_panel.add_child(btn_agri)

        # 发展商业
        btn_comm = Button(
            20 + btn_width + 20, 70, btn_width, btn_height,
            "发展商业", self.game.get_font('default'),
            COLORS['dark_blue'], COLORS['blue'], COLORS['white'],
            callback=self._on_develop_commerce
        )
        self.right_panel.add_child(btn_comm)

        # 加强城防
        btn_def = Button(
            20, 70 + spacing, btn_width, btn_height,
            "加强城防", self.game.get_font('default'),
            COLORS['dark_red'], COLORS['red'], COLORS['white'],
            callback=self._on_develop_defense
        )
        self.right_panel.add_child(btn_def)

        # 搜索人才
        btn_search = Button(
            20 + btn_width + 20, 70 + spacing, btn_width, btn_height,
            "搜索人才", self.game.get_font('default'),
            COLORS['purple'], COLORS['gold'], COLORS['white'],
            callback=self._on_search_officers
        )
        self.right_panel.add_child(btn_search)

        # 招降俘虏
        btn_recruit = Button(
            20, 70 + spacing * 2, btn_width, btn_height,
            "招降俘虏", self.game.get_font('default'),
            COLORS['brown'], COLORS['orange'], COLORS['white'],
            callback=self._on_recruit_prisoners
        )
        self.right_panel.add_child(btn_recruit)

        # 征兵
        btn_draft = Button(
            20 + btn_width + 20, 70 + spacing * 2, btn_width, btn_height,
            "征兵", self.game.get_font('default'),
            COLORS['dark_red'], COLORS['red'], COLORS['white'],
            callback=self._on_draft_troops
        )
        self.right_panel.add_child(btn_draft)

        # 出征
        btn_march = Button(
            20, 70 + spacing * 3, btn_width * 2 + 20, btn_height,
            "出征", self.game.get_font('default'),
            COLORS['gold'], (255, 255, 200), COLORS['dark_red'],
            callback=self._on_march
        )
        self.right_panel.add_child(btn_march)

        # 武将列表（示例数据）
        self.officers = [
            {"name": "刘备", "war": 75, "int": 78, "pol": 80},
            {"name": "关羽", "war": 98, "int": 76, "pol": 65},
            {"name": "张飞", "war": 99, "int": 30, "pol": 35},
        ]

    def on_enter(self, city=None):
        """进入场景"""
        super().on_enter()
        self.current_city = city or {'name': '未知城池', 'population': 10000}
        self._update_city_info()
        logger.info(f"进入城池: {self.current_city.get('name', '未知')}")

    def _update_city_info(self):
        """更新城池信息"""
        if self.current_city:
            self.city_name.set_text(self.current_city.get('name', '未知城池'))

    def _on_back(self):
        """返回大地图"""
        logger.info("返回大地图")
        self.game.change_scene('world_map')

    def _on_develop_agriculture(self):
        """开发农业"""
        logger.info("开发农业")

    def _on_develop_commerce(self):
        """发展商业"""
        logger.info("发展商业")

    def _on_develop_defense(self):
        """加强城防"""
        logger.info("加强城防")

    def _on_search_officers(self):
        """搜索人才"""
        logger.info("搜索人才")

    def _on_recruit_prisoners(self):
        """招降俘虏"""
        logger.info("招降俘虏")

    def _on_draft_troops(self):
        """征兵"""
        logger.info("征兵")

    def _on_march(self):
        """出征"""
        logger.info("出征")
        self.game.change_scene('battle')

    def handle_event(self, event):
        """处理事件"""
        self.ui_root.handle_event(event)

    def update(self, dt):
        """更新"""
        self.ui_root.update(dt)

    def render(self, screen):
        """渲染"""
        self.ui_root.render(screen)

        # 渲染武将列表
        self._render_officers(screen)

    def _render_officers(self, screen):
        """渲染武将列表"""
        abs_x, abs_y = self.middle_panel.get_absolute_pos()
        start_y = abs_y + 70

        for i, officer in enumerate(self.officers):
            y = start_y + i * 50
            if y > abs_y + self.middle_panel.rect.height - 50:
                break

            # 武将名称
            name_surface = self.game.get_font('default').render(
                f"{officer['name']}", True, COLORS['text']
            )
            screen.blit(name_surface, (abs_x + 20, y))

            # 属性
            attr_text = f"武:{officer['war']} 智:{officer['int']} 政:{officer['pol']}"
            attr_surface = self.game.get_font('small').render(attr_text, True, COLORS['gray'])
            screen.blit(attr_surface, (abs_x + 150, y + 5))
