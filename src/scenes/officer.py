"""
三国霸业游戏 - 武将信息场景
"""

import pygame
from scenes.base import BaseScene
from ui.base import Panel, Button, Label
from utils.constants import COLORS, SCREEN_WIDTH, SCREEN_HEIGHT
from utils.logger import get_logger
from core.officer import officer_manager
from core.faction import faction_manager
from core.city import city_manager

logger = get_logger('officer')


class OfficerScene(BaseScene):
    """武将信息场景"""

    def __init__(self, game):
        super().__init__(game)
        self.name = 'officer'
        self.current_officer = None
        self.return_scene = 'city'
        self.return_city = None

    def _init_scene(self):
        """初始化武将界面"""
        logger.info("初始化武将界面")

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

        # 武将名称
        self.officer_name_label = Label(300, 10, "武将名称", self.game.get_font('title'), COLORS['gold'])
        self.top_bar.add_child(self.officer_name_label)

        # 字
        self.courtesy_label = Label(500, 20, "字: --", self.game.get_font('default'), COLORS['white'])
        self.top_bar.add_child(self.courtesy_label)

        # 左侧属性面板
        self.left_panel = Panel(20, 80, 350, SCREEN_HEIGHT - 160, COLORS['panel_bg'])
        self.ui_root.add_child(self.left_panel)

        # 属性标题
        attr_title = Label(20, 20, "武将属性", self.game.get_font('large'), COLORS['dark_red'])
        self.left_panel.add_child(attr_title)

        # 武力
        self.war_label = Label(20, 70, "武力: 0", self.game.get_font('large'), COLORS['dark_red'])
        self.left_panel.add_child(self.war_label)

        # 智力
        self.int_label = Label(20, 110, "智力: 0", self.game.get_font('large'), COLORS['blue'])
        self.left_panel.add_child(self.int_label)

        # 政治
        self.pol_label = Label(20, 150, "政治: 0", self.game.get_font('large'), COLORS['green'])
        self.left_panel.add_child(self.pol_label)

        # 魅力
        self.chr_label = Label(20, 190, "魅力: 0", self.game.get_font('large'), COLORS['purple'])
        self.left_panel.add_child(self.chr_label)

        # 忠诚度和状态
        self.loyalty_label = Label(20, 250, "忠诚度: 0", self.game.get_font('default'), COLORS['text'])
        self.left_panel.add_child(self.loyalty_label)

        self.status_label = Label(20, 285, "状态: 空闲", self.game.get_font('default'), COLORS['text'])
        self.left_panel.add_child(self.status_label)

        # 中间信息面板
        self.middle_panel = Panel(390, 80, 400, SCREEN_HEIGHT - 160, COLORS['panel_bg'])
        self.ui_root.add_child(self.middle_panel)

        # 所属信息标题
        info_title = Label(20, 20, "所属信息", self.game.get_font('large'), COLORS['dark_red'])
        self.middle_panel.add_child(info_title)

        # 所属势力
        self.faction_label = Label(20, 70, "势力: --", self.game.get_font('default'), COLORS['text'])
        self.middle_panel.add_child(self.faction_label)

        # 所在城池
        self.city_label = Label(20, 105, "所在: --", self.game.get_font('default'), COLORS['text'])
        self.middle_panel.add_child(self.city_label)

        # 带兵数
        self.troops_label = Label(20, 140, "带兵: 0", self.game.get_font('default'), COLORS['text'])
        self.middle_panel.add_child(self.troops_label)

        # 技能标题
        skill_title = Label(20, 200, "技能", self.game.get_font('large'), COLORS['dark_red'])
        self.middle_panel.add_child(skill_title)

        # 技能列表
        self.skill_labels = []
        for i in range(4):
            skill_label = Label(20, 240 + i * 35, "", self.game.get_font('default'), COLORS['text'])
            self.skill_labels.append(skill_label)
            self.middle_panel.add_child(skill_label)

        # 右侧操作面板
        self.right_panel = Panel(810, 80, 450, SCREEN_HEIGHT - 160, COLORS['panel_bg'])
        self.ui_root.add_child(self.right_panel)

        # 操作标题
        action_title = Label(20, 20, "操作", self.game.get_font('large'), COLORS['dark_red'])
        self.right_panel.add_child(action_title)

        # 操作按钮
        btn_width = 120
        btn_height = 40
        spacing = 55

        # 调动按钮
        btn_transfer = Button(
            20, 70, btn_width, btn_height,
            "调动", self.game.get_font('default'),
            COLORS['dark_blue'], COLORS['blue'], COLORS['white'],
            callback=self._on_transfer
        )
        self.right_panel.add_child(btn_transfer)

        # 赏赐按钮（提高忠诚度）
        btn_reward = Button(
            20, 70 + spacing, btn_width, btn_height,
            "赏赐", self.game.get_font('default'),
            COLORS['dark_green'], COLORS['green'], COLORS['white'],
            callback=self._on_reward
        )
        self.right_panel.add_child(btn_reward)

        # 任命太守按钮
        btn_governor = Button(
            20, 70 + spacing * 2, btn_width, btn_height,
            "任命太守", self.game.get_font('default'),
            COLORS['purple'], COLORS['gold'], COLORS['white'],
            callback=self._on_appoint_governor
        )
        self.right_panel.add_child(btn_governor)

        # 出征按钮
        btn_march = Button(
            20, 70 + spacing * 3, btn_width, btn_height,
            "出征", self.game.get_font('default'),
            COLORS['dark_red'], COLORS['red'], COLORS['white'],
            callback=self._on_march
        )
        self.right_panel.add_child(btn_march)

        # 操作结果提示
        self.result_label = Label(20, 350, "", self.game.get_font('default'), COLORS['green'])
        self.right_panel.add_child(self.result_label)

    def on_enter(self, officer=None, return_scene='city', return_city=None):
        """进入场景"""
        super().on_enter()
        self.current_officer = officer
        self.return_scene = return_scene
        self.return_city = return_city
        self.result_label.set_text("")
        if officer:
            logger.info(f"查看武将: {officer.name}")
            self._update_officer_info()

    def _update_officer_info(self):
        """更新武将信息显示"""
        if not self.current_officer:
            return

        officer = self.current_officer

        # 更新名称
        self.officer_name_label.set_text(officer.name)

        # 更新字
        if officer.courtesy_name:
            self.courtesy_label.set_text(f"字: {officer.courtesy_name}")
        else:
            self.courtesy_label.set_text("")

        # 更新属性
        self.war_label.set_text(f"武力: {officer.attributes.war}")
        self.int_label.set_text(f"智力: {officer.attributes.intelligence}")
        self.pol_label.set_text(f"政治: {officer.attributes.politics}")
        self.chr_label.set_text(f"魅力: {officer.attributes.charisma}")

        # 更新忠诚度和状态
        self.loyalty_label.set_text(f"忠诚度: {officer.loyalty}")
        self.status_label.set_text(f"状态: {officer.get_status_text()}")

        # 更新所属信息
        faction = faction_manager.get_faction(officer.faction_id)
        if faction:
            self.faction_label.set_text(f"势力: {faction.name}")
        else:
            self.faction_label.set_text("势力: 在野")

        city = city_manager.get_city(officer.city_id)
        if city:
            self.city_label.set_text(f"所在: {city.name}")
        else:
            self.city_label.set_text("所在: 未知")

        self.troops_label.set_text(f"带兵: {officer.troops:,}")

        # 更新技能列表
        for i, label in enumerate(self.skill_labels):
            if i < len(officer.skills):
                label.set_text(f"• {officer.skills[i]}")
            else:
                label.set_text("")

    def _on_back(self):
        """返回"""
        logger.info("返回上级界面")
        if self.return_scene == 'city' and self.return_city:
            self.game.change_scene('city', self.return_city)
        else:
            self.game.change_scene(self.return_scene)

    def _on_transfer(self):
        """调动武将"""
        logger.info("调动武将")
        self.result_label.set_text("功能开发中...")
        self.result_label.color = COLORS['gray']

    def _on_reward(self):
        """赏赐武将，提高忠诚度"""
        if not self.current_officer:
            return

        # 检查是否属于玩家势力
        if self.current_officer.faction_id != self.game.faction_manager.player_faction_id:
            self.result_label.set_text("只能赏赐本势力武将")
            self.result_label.color = COLORS['red']
            return

        # 花费金钱提高忠诚度
        cost = 100
        player_faction = self.game.get_player_faction()
        if player_faction and player_faction.total_gold >= cost:
            player_faction.total_gold -= cost
            old_loyalty = self.current_officer.loyalty
            self.current_officer.loyalty = min(100, self.current_officer.loyalty + 5)
            gain = self.current_officer.loyalty - old_loyalty
            self.result_label.set_text(f"赏赐成功，忠诚度+{gain}")
            self.result_label.color = COLORS['green']
            self._update_officer_info()
        else:
            self.result_label.set_text("金钱不足")
            self.result_label.color = COLORS['red']

    def _on_appoint_governor(self):
        """任命为太守"""
        if not self.current_officer:
            return

        city = city_manager.get_city(self.current_officer.city_id)
        if city:
            city.governor_id = self.current_officer.id
            self.result_label.set_text(f"任命 {self.current_officer.name} 为 {city.name} 太守")
            self.result_label.color = COLORS['green']
        else:
            self.result_label.set_text("武将不在城中")
            self.result_label.color = COLORS['red']

    def _on_march(self):
        """出征"""
        logger.info("武将出征")
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
