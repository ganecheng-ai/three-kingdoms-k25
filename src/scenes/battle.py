"""
三国霸业游戏 - 战斗场景
"""

import pygame
import random
from scenes.base import BaseScene
from ui.base import Panel, Button, Label
from utils.constants import COLORS, SCREEN_WIDTH, SCREEN_HEIGHT
from utils.logger import get_logger
from core.officer import officer_manager
from core.city import city_manager

logger = get_logger('battle')


class BattleUnit:
    """战斗单位"""

    def __init__(self, officer_id, faction_id, x, y):
        self.officer_id = officer_id
        self.faction_id = faction_id
        self.x = x
        self.y = y
        self.troops = 0  # 当前兵力
        self.max_troops = 0  # 最大兵力
        self.selected = False
        self.has_moved = False
        self.has_acted = False

    @property
    def officer(self):
        """获取武将对象"""
        return officer_manager.get_officer(self.officer_id)

    def reset_turn(self):
        """重置回合状态"""
        self.has_moved = False
        self.has_acted = False

    def get_power(self):
        """获取战斗力"""
        if self.officer:
            base_power = self.officer.attributes.war * 2 + self.officer.attributes.intelligence
            return base_power * self.troops // 100
        return self.troops


class BattleScene(BaseScene):
    """战斗场景"""

    def __init__(self, game):
        super().__init__(game)
        self.name = 'battle'
        self.battle_state = 'selecting'  # selecting, moving, attacking, tactic
        self.turn = 1
        self.selected_unit = None
        self.units = []
        self.attacker_city = None
        self.defender_city = None

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
        self.attacker_label = Label(800, 15, "我军: 0", self.game.get_font('default'), COLORS['green'])
        self.top_bar.add_child(self.attacker_label)

        self.defender_label = Label(1000, 15, "敌军: 0", self.game.get_font('default'), COLORS['red'])
        self.top_bar.add_child(self.defender_label)

        # 状态提示
        self.status_label = Label(50, 15, "选择单位", self.game.get_font('small'), COLORS['yellow'])
        self.top_bar.add_child(self.status_label)

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

        # 初始化战斗单位
        self._init_battle_units()

    def _init_battle_units(self):
        """初始化战斗单位"""
        self.units = []
        player_faction = self.game.faction_manager.player_faction_id

        # 获取玩家城池的武将作为攻击方
        if self.attacker_city:
            for oid in self.attacker_city.officer_ids[:3]:  # 最多3个武将
                officer = officer_manager.get_officer(oid)
                if officer:
                    unit = BattleUnit(oid, player_faction, 100 + len(self.units) * 50, 150 + len(self.units) * 50)
                    unit.troops = officer.troops if officer.troops > 0 else 5000
                    unit.max_troops = unit.troops
                    self.units.append(unit)

        # 如果没有攻击单位，创建默认单位
        if not self.units:
            self.units = [
                BattleUnit(4, player_faction, 100, 150),   # 关羽
                BattleUnit(5, player_faction, 150, 200),   # 张飞
                BattleUnit(6, player_faction, 200, 250),   # 赵云
            ]
            for unit in self.units:
                unit.troops = 5000
                unit.max_troops = 5000

        # 创建敌方单位
        enemy_faction = 1 if player_faction != 1 else 2  # 简单的敌对势力
        enemy_units = [
            BattleUnit(1, enemy_faction, 700, 150),    # 曹操
            BattleUnit(3, enemy_faction, 750, 200),    # 张辽
            BattleUnit(2, enemy_faction, 800, 250),    # 司马懿
        ]
        for unit in enemy_units:
            unit.troops = 5000
            unit.max_troops = 5000
        self.units.extend(enemy_units)

        self._update_battle_info()

    def _update_battle_info(self):
        """更新战斗信息"""
        player_faction = self.game.faction_manager.player_faction_id
        player_troops = sum(u.troops for u in self.units if u.faction_id == player_faction)
        enemy_troops = sum(u.troops for u in self.units if u.faction_id != player_faction)

        self.attacker_label.set_text(f"我军: {player_troops:,}")
        self.defender_label.set_text(f"敌军: {enemy_troops:,}")
        self.turn_label.set_text(f"第 {self.turn} 回合")

    def on_enter(self, attacker_city=None, defender_city=None):
        """进入战斗场景"""
        super().on_enter()
        self.attacker_city = attacker_city
        self.defender_city = defender_city
        self.turn = 1
        self.selected_unit = None
        self.battle_state = 'selecting'

        if attacker_city and defender_city:
            self.battle_title.set_text(f"{attacker_city.name} vs {defender_city.name}")
            logger.info(f"战斗开始: {attacker_city.name} 攻打 {defender_city.name}")

        self._init_battle_units()

    def _on_retreat(self):
        """撤退"""
        logger.info("撤退")
        self.game.change_scene('world_map')

    def _on_move(self):
        """移动"""
        if self.selected_unit:
            self.battle_state = 'moving'
            self.status_label.set_text("选择移动目标")
            self.status_label.color = COLORS['blue']
            logger.info("移动指令")
        else:
            self.status_label.set_text("请先选择单位")
            self.status_label.color = COLORS['red']

    def _on_attack(self):
        """攻击"""
        if self.selected_unit:
            self.battle_state = 'attacking'
            self.status_label.set_text("选择攻击目标")
            self.status_label.color = COLORS['red']
            logger.info("攻击指令")
        else:
            self.status_label.set_text("请先选择单位")
            self.status_label.color = COLORS['red']

    def _on_tactic(self):
        """计策"""
        logger.info("计策指令")
        self.status_label.set_text("计策: 功能开发中")
        self.status_label.color = COLORS['purple']

    def _on_formation(self):
        """阵型"""
        logger.info("阵型指令")
        self.status_label.set_text("阵型: 功能开发中")
        self.status_label.color = COLORS['orange']

    def _on_wait(self):
        """待机"""
        if self.selected_unit:
            self.selected_unit.has_moved = True
            self.selected_unit.has_acted = True
            self.selected_unit.selected = False
            self.selected_unit = None
            self.battle_state = 'selecting'
            self.status_label.set_text("选择单位")
            self.status_label.color = COLORS['yellow']
            logger.info("待机指令")

    def _on_auto(self):
        """自动战斗"""
        logger.info("自动战斗")
        self.status_label.set_text("自动战斗中...")
        self.status_label.color = COLORS['green']

        # 简单的自动战斗逻辑
        player_faction = self.game.faction_manager.player_faction_id
        player_units = [u for u in self.units if u.faction_id == player_faction and u.troops > 0]
        enemy_units = [u for u in self.units if u.faction_id != player_faction and u.troops > 0]

        if player_units and enemy_units:
            # 随机选择一个敌方单位造成伤害
            target = random.choice(enemy_units)
            attacker = random.choice(player_units)
            damage = attacker.get_power() // 10 + random.randint(100, 500)
            target.troops = max(0, target.troops - damage)
            logger.info(f"自动战斗: {attacker.officer.name if attacker.officer else '我军'} 对 {target.officer.name if target.officer else '敌军'} 造成 {damage} 伤害")

        self._check_battle_end()
        self._update_battle_info()

    def _on_end_turn(self):
        """回合结束"""
        logger.info("战斗回合结束")
        self.turn += 1
        self.selected_unit = None
        self.battle_state = 'selecting'
        self.status_label.set_text("选择单位")
        self.status_label.color = COLORS['yellow']

        # AI回合
        self._ai_turn()

        # 重置所有单位状态
        for unit in self.units:
            unit.reset_turn()

        self._check_battle_end()
        self._update_battle_info()

    def _ai_turn(self):
        """AI回合"""
        player_faction = self.game.faction_manager.player_faction_id
        ai_units = [u for u in self.units if u.faction_id != player_faction and u.troops > 0]
        player_units = [u for u in self.units if u.faction_id == player_faction and u.troops > 0]

        for unit in ai_units:
            if player_units:
                # AI随机攻击玩家单位
                target = random.choice(player_units)
                damage = unit.get_power() // 10 + random.randint(100, 500)
                target.troops = max(0, target.troops - damage)
                logger.info(f"AI行动: {unit.officer.name if unit.officer else '敌军'} 攻击 {target.officer.name if target.officer else '我军'} 造成 {damage} 伤害")

    def _check_battle_end(self):
        """检查战斗是否结束"""
        player_faction = self.game.faction_manager.player_faction_id
        player_alive = any(u.troops > 0 for u in self.units if u.faction_id == player_faction)
        enemy_alive = any(u.troops > 0 for u in self.units if u.faction_id != player_faction)

        if not player_alive:
            self.status_label.set_text("战斗失败!")
            self.status_label.color = COLORS['red']
            logger.info("战斗失败")
        elif not enemy_alive:
            self.status_label.set_text("战斗胜利!")
            self.status_label.color = COLORS['gold']
            logger.info("战斗胜利")

    def _get_unit_at(self, x, y):
        """获取指定位置的单位"""
        for unit in self.units:
            if unit.troops <= 0:
                continue
            unit_x = self.battlefield.left + unit.x
            unit_y = self.battlefield.top + unit.y
            dx = x - unit_x
            dy = y - unit_y
            if dx * dx + dy * dy <= 400:  # 20像素半径
                return unit
        return None

    def handle_event(self, event):
        """处理事件"""
        self.ui_root.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = event.pos

            # 检查是否点击在战场内
            if self.battlefield.collidepoint(mouse_x, mouse_y):
                clicked_unit = self._get_unit_at(mouse_x, mouse_y)

                if self.battle_state == 'selecting':
                    # 选择单位
                    if clicked_unit and clicked_unit.troops > 0:
                        # 取消之前的选择
                        if self.selected_unit:
                            self.selected_unit.selected = False

                        self.selected_unit = clicked_unit
                        self.selected_unit.selected = True
                        officer = clicked_unit.officer
                        name = officer.name if officer else "未知"
                        self.status_label.set_text(f"选中: {name}")
                        self.status_label.color = COLORS['green']
                        logger.info(f"选择单位: {name}")

                elif self.battle_state == 'moving':
                    # 移动单位
                    if self.selected_unit and not self.selected_unit.has_moved:
                        # 计算相对位置
                        new_x = mouse_x - self.battlefield.left
                        new_y = mouse_y - self.battlefield.top

                        # 限制移动范围（每回合最多移动100像素）
                        dx = new_x - self.selected_unit.x
                        dy = new_y - self.selected_unit.y
                        dist = (dx * dx + dy * dy) ** 0.5

                        if dist <= 100 and clicked_unit is None:
                            self.selected_unit.x = new_x
                            self.selected_unit.y = new_y
                            self.selected_unit.has_moved = True
                            self.battle_state = 'selecting'
                            self.status_label.set_text("移动完成，选择单位")
                            self.status_label.color = COLORS['yellow']
                            officer = self.selected_unit.officer
                            logger.info(f"移动单位: {officer.name if officer else '未知'}")
                        else:
                            self.status_label.set_text("移动范围不足或有阻挡")
                            self.status_label.color = COLORS['red']

                elif self.battle_state == 'attacking':
                    # 攻击
                    if self.selected_unit and not self.selected_unit.has_acted and clicked_unit:
                        # 检查是否可以攻击（不同势力）
                        if clicked_unit.faction_id != self.selected_unit.faction_id:
                            # 计算伤害
                            damage = self.selected_unit.get_power() // 10 + random.randint(100, 500)
                            clicked_unit.troops = max(0, clicked_unit.troops - damage)

                            attacker = self.selected_unit.officer
                            target = clicked_unit.officer
                            attacker_name = attacker.name if attacker else "我军"
                            target_name = target.name if target else "敌军"

                            self.status_label.set_text(f"{attacker_name} 对 {target_name} 造成 {damage} 伤害!")
                            self.status_label.color = COLORS['red']
                            logger.info(f"攻击: {attacker_name} -> {target_name}, 伤害: {damage}")

                            self.selected_unit.has_acted = True
                            self.battle_state = 'selecting'
                            self._check_battle_end()
                            self._update_battle_info()
                        else:
                            self.status_label.set_text("不能攻击友军")
                            self.status_label.color = COLORS['red']

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

        # 渲染移动范围提示
        if self.battle_state == 'moving' and self.selected_unit and not self.selected_unit.has_moved:
            self._render_move_range(screen)

        # 渲染攻击范围提示
        if self.battle_state == 'attacking' and self.selected_unit and not self.selected_unit.has_acted:
            self._render_attack_range(screen)

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
        player_faction = self.game.faction_manager.player_faction_id

        for unit in self.units:
            if unit.troops <= 0:
                continue

            x = self.battlefield.left + unit.x
            y = self.battlefield.top + unit.y

            # 根据势力选择颜色
            if unit.faction_id == player_faction:
                color = COLORS['green']
            else:
                color = COLORS['red']

            # 选中高亮
            if unit.selected:
                pygame.draw.circle(screen, COLORS['yellow'], (x, y), 25)

            # 绘制单位（圆形）
            pygame.draw.circle(screen, color, (x, y), 20)
            pygame.draw.circle(screen, COLORS['black'], (x, y), 20, 2)

            # 单位名称
            officer = unit.officer
            name = officer.name if officer else "未知"
            name_surface = self.game.get_font('small').render(name, True, COLORS['white'])
            name_rect = name_surface.get_rect(center=(x, y - 5))
            screen.blit(name_surface, name_rect)

            # 兵力
            troop_text = f"{unit.troops // 1000}k"
            troop_surface = self.game.get_font('small').render(troop_text, True, COLORS['white'])
            troop_rect = troop_surface.get_rect(center=(x, y + 10))
            screen.blit(troop_surface, troop_rect)

            # 行动状态指示
            if unit.has_moved and unit.has_acted:
                pygame.draw.circle(screen, COLORS['gray'], (x + 15, y - 15), 5)

    def _render_move_range(self, screen):
        """渲染移动范围"""
        if not self.selected_unit:
            return

        x = self.battlefield.left + self.selected_unit.x
        y = self.battlefield.top + self.selected_unit.y

        # 绘制移动范围圆圈（100像素半径）
        pygame.draw.circle(screen, COLORS['blue'], (x, y), 100, 2)
        pygame.draw.circle(screen, (*COLORS['blue'][:3], 50), (x, y), 100)

    def _render_attack_range(self, screen):
        """渲染攻击范围"""
        if not self.selected_unit:
            return

        x = self.battlefield.left + self.selected_unit.x
        y = self.battlefield.top + self.selected_unit.y

        # 绘制攻击范围圆圈（150像素半径）
        pygame.draw.circle(screen, COLORS['red'], (x, y), 150, 2)
        pygame.draw.circle(screen, (*COLORS['red'][:3], 50), (x, y), 150)
