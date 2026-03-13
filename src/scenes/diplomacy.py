"""
三国霸业游戏 - 外交场景
"""

import pygame
from scenes.base import BaseScene
from ui.base import Panel, Button, Label, ScrollPanel
from ui.dialog import show_message, show_confirm
from utils.constants import COLORS, SCREEN_WIDTH, SCREEN_HEIGHT, FACTION_COLORS
from utils.logger import get_logger
from core.faction import faction_manager, FACTION_NAMES

logger = get_logger('diplomacy')


class DiplomacyScene(BaseScene):
    """外交场景"""

    def __init__(self, game):
        super().__init__(game)
        self.name = 'diplomacy'
        self.selected_faction_id = None
        self.faction_buttons = []

    def _init_scene(self):
        """初始化外交界面"""
        logger.info("初始化外交界面")

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

        # 标题
        self.title_label = Label(300, 15, "外交事务", self.game.get_font('large'), COLORS['gold'])
        self.top_bar.add_child(self.title_label)

        # 当前日期
        self.date_label = Label(550, 15, "", self.game.get_font('default'), COLORS['white'])
        self.top_bar.add_child(self.date_label)

        # 左侧势力列表
        self.left_panel = Panel(20, 80, 300, SCREEN_HEIGHT - 160, COLORS['panel_bg'])
        self.ui_root.add_child(self.left_panel)

        self.faction_list_title = Label(20, 20, "势力列表", self.game.get_font('large'), COLORS['dark_red'])
        self.left_panel.add_child(self.faction_list_title)

        # 势力列表容器
        self.faction_list_container = Panel(20, 60, 260, SCREEN_HEIGHT - 240, (40, 40, 40))
        self.left_panel.add_child(self.faction_list_container)

        # 右侧详情面板
        self.right_panel = Panel(340, 80, SCREEN_WIDTH - 360, SCREEN_HEIGHT - 160, COLORS['panel_bg'])
        self.ui_root.add_child(self.right_panel)

        self.detail_title = Label(20, 20, "势力详情", self.game.get_font('large'), COLORS['dark_red'])
        self.right_panel.add_child(self.detail_title)

        # 详情标签
        self.detail_name_label = Label(20, 60, "势力: --", self.game.get_font('default'), COLORS['text'])
        self.right_panel.add_child(self.detail_name_label)

        self.detail_leader_label = Label(20, 90, "君主: --", self.game.get_font('default'), COLORS['text'])
        self.right_panel.add_child(self.detail_leader_label)

        self.detail_cities_label = Label(20, 120, "城池: 0", self.game.get_font('default'), COLORS['text'])
        self.right_panel.add_child(self.detail_cities_label)

        self.detail_troops_label = Label(20, 150, "兵力: 0", self.game.get_font('default'), COLORS['text'])
        self.right_panel.add_child(self.detail_troops_label)

        self.detail_relation_label = Label(20, 180, "关系: 中立", self.game.get_font('default'), COLORS['text'])
        self.right_panel.add_child(self.detail_relation_label)

        self.detail_power_label = Label(20, 210, "势力评分: 0", self.game.get_font('default'), COLORS['text'])
        self.right_panel.add_child(self.detail_power_label)

        # 外交操作按钮
        self.action_title = Label(20, 260, "外交操作", self.game.get_font('large'), COLORS['dark_red'])
        self.right_panel.add_child(self.action_title)

        btn_width = 120
        btn_height = 40

        # 同盟按钮
        self.btn_alliance = Button(
            20, 310, btn_width, btn_height,
            "提议同盟", self.game.get_font('default'),
            COLORS['dark_green'], COLORS['green'], COLORS['white'],
            callback=self._on_propose_alliance
        )
        self.right_panel.add_child(self.btn_alliance)

        # 断交按钮
        self.btn_break = Button(
            160, 310, btn_width, btn_height,
            "断绝关系", self.game.get_font('default'),
            COLORS['dark_red'], COLORS['red'], COLORS['white'],
            callback=self._on_break_relation
        )
        self.right_panel.add_child(self.btn_break)

        # 改善关系按钮
        self.btn_improve = Button(
            300, 310, btn_width, btn_height,
            "赠送礼物", self.game.get_font('default'),
            COLORS['dark_blue'], COLORS['blue'], COLORS['white'],
            callback=self._on_gift
        )
        self.right_panel.add_child(self.btn_improve)

        # 劝降按钮
        self.btn_surrender = Button(
            20, 370, btn_width, btn_height,
            "劝降", self.game.get_font('default'),
            COLORS['purple'], COLORS['gold'], COLORS['white'],
            callback=self._on_surrender
        )
        self.right_panel.add_child(self.btn_surrender)

        # 宣战按钮
        self.btn_war = Button(
            160, 370, btn_width, btn_height,
            "宣战", self.game.get_font('default'),
            (100, 0, 0), (150, 0, 0), COLORS['white'],
            callback=self._on_declare_war
        )
        self.right_panel.add_child(self.btn_war)

        # 外交关系说明
        self.relation_info = Label(20, 440, "关系说明: 敌对(<-50) 中立(-50~50) 友好(>50) 同盟(>70)",
                                    self.game.get_font('small'), COLORS['light_gray'])
        self.right_panel.add_child(self.relation_info)

        self._update_display()
        self._create_faction_list()

    def on_enter(self, *args, **kwargs):
        """进入场景"""
        super().on_enter(*args, **kwargs)
        self._update_display()
        self._create_faction_list()

    def _update_display(self):
        """更新显示信息"""
        self.date_label.set_text(self.game.get_formatted_date())
        self._update_faction_details()

    def _create_faction_list(self):
        """创建势力列表"""
        # 清空旧按钮
        self.faction_buttons.clear()
        self.faction_list_container.children.clear()

        player_faction = self.game.get_player_faction()
        if not player_faction:
            return

        # 获取其他势力（排除玩家自己和中立）
        other_factions = [f for f in faction_manager.get_all_factions()
                         if f.id != player_faction.id and f.id != 0]

        y_offset = 10
        for faction in other_factions:
            relation = player_faction.get_diplomatic_relation(faction.id)
            relation_text = self._get_relation_text(relation)

            # 势力按钮
            btn = Button(
                10, y_offset, 240, 35,
                f"{faction.name} [{relation_text}]", self.game.get_font('small'),
                FACTION_COLORS.get(faction.id, (100, 100, 100)),
                (min(c + 30, 255) for c in FACTION_COLORS.get(faction.id, (100, 100, 100))),
                COLORS['white'],
                callback=lambda fid=faction.id: self._on_select_faction(fid)
            )
            self.faction_list_container.add_child(btn)
            self.faction_buttons.append((faction.id, btn))
            y_offset += 45

    def _get_relation_text(self, relation: int) -> str:
        """获取关系文本描述"""
        if relation > 70:
            return "同盟"
        elif relation > 50:
            return "友好"
        elif relation > -50:
            return "中立"
        else:
            return "敌对"

    def _get_relation_color(self, relation: int) -> tuple:
        """获取关系颜色"""
        if relation > 70:
            return COLORS['green']
        elif relation > 50:
            return (100, 255, 100)
        elif relation > -50:
            return COLORS['yellow']
        else:
            return COLORS['red']

    def _on_select_faction(self, faction_id: int):
        """选择势力"""
        self.selected_faction_id = faction_id
        self._update_faction_details()

        # 更新按钮选中状态
        for fid, btn in self.faction_buttons:
            if fid == faction_id:
                btn.border_color = COLORS['gold']
                btn.border_width = 3
            else:
                btn.border_color = COLORS['black']
                btn.border_width = 1

    def _update_faction_details(self):
        """更新势力详情显示"""
        if self.selected_faction_id is None:
            self.detail_name_label.set_text("势力: --")
            self.detail_leader_label.set_text("君主: --")
            self.detail_cities_label.set_text("城池: 0")
            self.detail_troops_label.set_text("兵力: 0")
            self.detail_relation_label.set_text("关系: --")
            self.detail_power_label.set_text("势力评分: 0")
            return

        faction = faction_manager.get_faction(self.selected_faction_id)
        player_faction = self.game.get_player_faction()

        if faction and player_faction:
            # 更新资源统计
            faction.update_resources(self.game.city_manager.cities)

            # 获取君主名
            leader_name = "未知"
            if faction.leader_id > 0:
                leader = self.game.officer_manager.get_officer(faction.leader_id)
                if leader:
                    leader_name = leader.name

            relation = player_faction.get_diplomatic_relation(faction.id)
            relation_text = self._get_relation_text(relation)

            self.detail_name_label.set_text(f"势力: {faction.name}")
            self.detail_name_label.color = faction.color
            self.detail_leader_label.set_text(f"君主: {leader_name}")
            self.detail_cities_label.set_text(f"城池: {len(faction.city_ids)}")
            self.detail_troops_label.set_text(f"兵力: {faction.total_troops}")
            self.detail_relation_label.set_text(f"关系: {relation_text} ({relation})")
            self.detail_relation_label.color = self._get_relation_color(relation)
            self.detail_power_label.set_text(f"势力评分: {faction.get_power_score()}")

    def _on_propose_alliance(self):
        """提议同盟"""
        if self.selected_faction_id is None:
            show_message(self.ui_root, "请先选择一个势力", self.game.get_font('default'))
            return

        player_faction = self.game.get_player_faction()
        target_faction = faction_manager.get_faction(self.selected_faction_id)

        if not player_faction or not target_faction:
            return

        # 检查当前关系
        relation = player_faction.get_diplomatic_relation(self.selected_faction_id)

        if relation > 70:
            show_message(self.ui_root, f"已经与 {target_faction.name} 结盟", self.game.get_font('default'))
            return

        if relation < 30:
            show_message(self.ui_root, f"与 {target_faction.name} 关系不佳，无法结盟", self.game.get_font('default'))
            return

        # 计算成功率
        success_chance = (relation + 50) / 120  # 关系越好成功率越高
        import random
        if random.random() < success_chance:
            faction_manager.form_alliance(player_faction.id, self.selected_faction_id)
            show_message(self.ui_root, f"成功与 {target_faction.name} 建立同盟！", self.game.get_font('default'))
            logger.info(f"玩家与 {target_faction.name} 建立同盟")
        else:
            show_message(self.ui_root, f"{target_faction.name} 拒绝了同盟提议", self.game.get_font('default'))
            # 关系略微下降
            faction_manager.improve_relation(player_faction.id, self.selected_faction_id, -5)

        self._create_faction_list()
        self._update_faction_details()

    def _on_break_relation(self):
        """断绝关系"""
        if self.selected_faction_id is None:
            show_message(self.ui_root, "请先选择一个势力", self.game.get_font('default'))
            return

        player_faction = self.game.get_player_faction()
        target_faction = faction_manager.get_faction(self.selected_faction_id)

        if not player_faction or not target_faction:
            return

        def do_break():
            faction_manager.improve_relation(player_faction.id, self.selected_faction_id, -100)
            show_message(self.ui_root, f"已断绝与 {target_faction.name} 的关系", self.game.get_font('default'))
            logger.info(f"玩家断绝与 {target_faction.name} 的关系")
            self._create_faction_list()
            self._update_faction_details()

        show_confirm(self.ui_root,
                    f"确定要断绝与 {target_faction.name} 的关系吗？",
                    self.game.get_font('default'),
                    on_confirm=do_break)

    def _on_gift(self):
        """赠送礼物改善关系"""
        if self.selected_faction_id is None:
            show_message(self.ui_root, "请先选择一个势力", self.game.get_font('default'))
            return

        player_faction = self.game.get_player_faction()
        target_faction = faction_manager.get_faction(self.selected_faction_id)

        if not player_faction or not target_faction:
            return

        # 检查金钱
        if player_faction.total_gold < 1000:
            show_message(self.ui_root, "金钱不足，需要1000金", self.game.get_font('default'))
            return

        # 扣除金钱
        # 从第一个城池扣除
        player_cities = self.game.get_player_cities()
        if player_cities:
            player_cities[0].resources.gold -= 1000

        # 改善关系
        faction_manager.improve_relation(player_faction.id, self.selected_faction_id, 15)
        show_message(self.ui_root, f"向 {target_faction.name} 赠送礼物，关系得到改善", self.game.get_font('default'))
        logger.info(f"玩家向 {target_faction.name} 赠送礼物")

        self._create_faction_list()
        self._update_faction_details()

    def _on_surrender(self):
        """劝降"""
        if self.selected_faction_id is None:
            show_message(self.ui_root, "请先选择一个势力", self.game.get_font('default'))
            return

        player_faction = self.game.get_player_faction()
        target_faction = faction_manager.get_faction(self.selected_faction_id)

        if not player_faction or not target_faction:
            return

        # 劝降条件检查
        if len(target_faction.city_ids) > 3:
            show_message(self.ui_root, f"{target_faction.name} 势力尚强，无法劝降", self.game.get_font('default'))
            return

        if target_faction.total_troops > 50000:
            show_message(self.ui_root, f"{target_faction.name} 兵力尚多，无法劝降", self.game.get_font('default'))
            return

        relation = player_faction.get_diplomatic_relation(self.selected_faction_id)
        if relation < 0:
            show_message(self.ui_root, f"与 {target_faction.name} 关系不佳，无法劝降", self.game.get_font('default'))
            return

        # 计算劝降成功率
        player_power = player_faction.get_power_score()
        target_power = target_faction.get_power_score()
        power_ratio = target_power / max(player_power, 1)

        base_chance = 0.3  # 基础成功率30%
        relation_bonus = relation / 200  # 关系加成
        power_bonus = (1 - power_ratio) * 0.4  # 实力差距加成

        success_chance = base_chance + relation_bonus + power_bonus
        success_chance = max(0.1, min(0.9, success_chance))  # 限制在10%-90%

        import random
        if random.random() < success_chance:
            # 劝降成功
            show_message(self.ui_root,
                        f"{target_faction.name} 接受劝降，归顺我方！",
                        self.game.get_font('default'))
            logger.info(f"玩家成功劝降 {target_faction.name}")

            # 转移城池所有权
            for city_id in target_faction.city_ids[:]:
                city = self.game.city_manager.get_city(city_id)
                if city:
                    city.faction_id = player_faction.id
                    player_faction.add_city(city_id)

            # 转移武将
            for officer_id in target_faction.officer_ids[:]:
                officer = self.game.officer_manager.get_officer(officer_id)
                if officer:
                    officer.faction_id = player_faction.id
                    officer.loyalty = 50  # 降将忠诚度降低
                    player_faction.add_officer(officer_id)

            # 增加资源
            player_faction.total_gold += target_faction.total_gold // 2
            player_faction.total_food += target_faction.total_food // 2

            # 移除被劝降势力
            if self.selected_faction_id in faction_manager.factions:
                del faction_manager.factions[self.selected_faction_id]

            self.selected_faction_id = None
        else:
            show_message(self.ui_root,
                        f"{target_faction.name} 拒绝劝降，关系恶化",
                        self.game.get_font('default'))
            faction_manager.improve_relation(player_faction.id, self.selected_faction_id, -20)

        self._create_faction_list()
        self._update_faction_details()

    def _on_declare_war(self):
        """宣战"""
        if self.selected_faction_id is None:
            show_message(self.ui_root, "请先选择一个势力", self.game.get_font('default'))
            return

        player_faction = self.game.get_player_faction()
        target_faction = faction_manager.get_faction(self.selected_faction_id)

        if not player_faction or not target_faction:
            return

        def do_war():
            faction_manager.declare_war(player_faction.id, self.selected_faction_id)
            show_message(self.ui_root, f"已向 {target_faction.name} 宣战！", self.game.get_font('default'))
            logger.info(f"玩家向 {target_faction.name} 宣战")
            self._create_faction_list()
            self._update_faction_details()

        show_confirm(self.ui_root,
                    f"确定要向 {target_faction.name} 宣战吗？",
                    self.game.get_font('default'),
                    on_confirm=do_war)

    def _on_back(self):
        """返回大地图"""
        self.game.change_scene('world_map')

    def handle_event(self, event):
        """处理事件"""
        self.ui_root.handle_event(event)

    def update(self, dt):
        """更新"""
        self.ui_root.update(dt)

    def render(self, screen):
        """渲染"""
        self.ui_root.render(screen)
