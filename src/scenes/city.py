"""
三国霸业游戏 - 城市管理场景
"""

import pygame
from scenes.base import BaseScene
from ui.base import Panel, Button, Label
from utils.constants import COLORS, SCREEN_WIDTH, SCREEN_HEIGHT
from utils.logger import get_logger
from core.city import city_manager
from core.officer import officer_manager
from core.faction import faction_manager

logger = get_logger('city')


class CityScene(BaseScene):
    """城市界面场景"""

    def __init__(self, game):
        super().__init__(game)
        self.name = 'city'
        self.current_city = None
        self.officer_click_rects = []  # 存储武将点击区域

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
        self.city_name_label = Label(300, 15, "城池名称", self.game.get_font('large'), COLORS['gold'])
        self.top_bar.add_child(self.city_name_label)

        # 所属势力
        self.faction_label = Label(550, 15, "势力: --", self.game.get_font('default'), COLORS['white'])
        self.top_bar.add_child(self.faction_label)

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

        # 预计收入
        self.income_title = Label(20, 280, "月度预计", self.game.get_font('default'), COLORS['dark_red'])
        self.left_panel.add_child(self.income_title)

        self.gold_income_label = Label(20, 310, "金钱收入: 0", self.game.get_font('small'), COLORS['green'])
        self.left_panel.add_child(self.gold_income_label)

        self.food_income_label = Label(20, 335, "粮草收入: 0", self.game.get_font('small'), COLORS['green'])
        self.left_panel.add_child(self.food_income_label)

        self.gold_cost_label = Label(20, 360, "金钱消耗: 0", self.game.get_font('small'), COLORS['red'])
        self.left_panel.add_child(self.gold_cost_label)

        self.food_cost_label = Label(20, 385, "粮草消耗: 0", self.game.get_font('small'), COLORS['red'])
        self.left_panel.add_child(self.food_cost_label)

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

        # 操作结果提示
        self.result_label = Label(20, 300, "", self.game.get_font('default'), COLORS['green'])
        self.right_panel.add_child(self.result_label)

        # 武将列表滚动偏移
        self.officers_scroll_offset = 0

    def on_enter(self, city=None):
        """进入场景"""
        super().on_enter()
        self.current_city = city
        self._update_city_info()
        self.result_label.set_text("")
        if city:
            logger.info(f"进入城池: {city.name}")

    def _update_city_info(self):
        """更新城池信息显示"""
        if not self.current_city:
            return

        city = self.current_city

        # 更新名称
        self.city_name_label.set_text(city.name)

        # 更新所属势力
        faction = faction_manager.get_faction(city.faction_id)
        if faction:
            self.faction_label.set_text(f"势力: {faction.name}")

        # 更新属性
        self.population_label.set_text(f"人口: {city.population:,}")
        self.agriculture_label.set_text(f"农业: {city.agriculture}/100")
        self.commerce_label.set_text(f"商业: {city.commerce}/100")
        self.defense_label.set_text(f"城防: {city.defense}/100")
        self.gold_label.set_text(f"金钱: {city.resources.gold:,}")
        self.food_label.set_text(f"粮草: {city.resources.food:,}")
        self.troops_label.set_text(f"兵力: {city.troops:,}")

        # 更新收入预期
        gold_income, food_income = city.get_monthly_income()
        gold_cost, food_cost = city.get_monthly_consumption()

        self.gold_income_label.set_text(f"金钱收入: +{gold_income:,}")
        self.food_income_label.set_text(f"粮草收入: +{food_income:,}")
        self.gold_cost_label.set_text(f"金钱消耗: -{gold_cost:,}")
        self.food_cost_label.set_text(f"粮草消耗: -{food_cost:,}")

        # 更新武将列表标题
        officer_count = len(city.officer_ids)
        self.officers_title.set_text(f"城中武将 ({officer_count})")

    def _on_back(self):
        """返回大地图"""
        logger.info("返回大地图")
        self.game.change_scene('world_map')

    def _on_develop_agriculture(self):
        """开发农业"""
        if not self.current_city:
            return

        # 找一个政治高的武将来执行
        best_officer = None
        best_pol = 0
        for oid in self.current_city.officer_ids:
            officer = officer_manager.get_officer(oid)
            if officer and officer.attributes.politics > best_pol:
                best_pol = officer.attributes.politics
                best_officer = officer

        if best_officer:
            result = self.current_city.develop_agriculture(
                best_officer.attributes.intelligence,
                best_officer.attributes.politics
            )
            if result > 0:
                self.result_label.set_text(f"{best_officer.name} 成功开发农业，增加 {result} 点")
                self.result_label.color = COLORS['green']
            else:
                self.result_label.set_text(f"{best_officer.name} 开发农业失败")
                self.result_label.color = COLORS['red']
        else:
            self.result_label.set_text("没有武将可以执行此操作")
            self.result_label.color = COLORS['red']

        self._update_city_info()

    def _on_develop_commerce(self):
        """发展商业"""
        if not self.current_city:
            return

        best_officer = None
        best_pol = 0
        for oid in self.current_city.officer_ids:
            officer = officer_manager.get_officer(oid)
            if officer and officer.attributes.politics > best_pol:
                best_pol = officer.attributes.politics
                best_officer = officer

        if best_officer:
            result = self.current_city.develop_commerce(
                best_officer.attributes.intelligence,
                best_officer.attributes.politics
            )
            if result > 0:
                self.result_label.set_text(f"{best_officer.name} 成功发展商业，增加 {result} 点")
                self.result_label.color = COLORS['green']
            else:
                self.result_label.set_text(f"{best_officer.name} 发展商业失败")
                self.result_label.color = COLORS['red']
        else:
            self.result_label.set_text("没有武将可以执行此操作")
            self.result_label.color = COLORS['red']

        self._update_city_info()

    def _on_develop_defense(self):
        """加强城防"""
        if not self.current_city:
            return

        best_officer = None
        best_pol = 0
        for oid in self.current_city.officer_ids:
            officer = officer_manager.get_officer(oid)
            if officer and officer.attributes.politics > best_pol:
                best_pol = officer.attributes.politics
                best_officer = officer

        if best_officer:
            result = self.current_city.develop_defense(
                best_officer.attributes.intelligence,
                best_officer.attributes.politics
            )
            if result > 0:
                self.result_label.set_text(f"{best_officer.name} 成功加强城防，增加 {result} 点")
                self.result_label.color = COLORS['green']
            else:
                self.result_label.set_text(f"{best_officer.name} 加强城防失败")
                self.result_label.color = COLORS['red']
        else:
            self.result_label.set_text("没有武将可以执行此操作")
            self.result_label.color = COLORS['red']

        self._update_city_info()

    def _on_search_officers(self):
        """搜索人才"""
        if not self.current_city:
            return

        best_officer = None
        best_int = 0
        for oid in self.current_city.officer_ids:
            officer = officer_manager.get_officer(oid)
            if officer and officer.attributes.intelligence > best_int:
                best_int = officer.attributes.intelligence
                best_officer = officer

        if best_officer:
            found = officer_manager.search_officers(self.current_city.id)
            if found:
                found.city_id = self.current_city.id
                self.current_city.add_officer(found.id)
                self.result_label.set_text(f"{best_officer.name} 搜索到武将: {found.name}")
                self.result_label.color = COLORS['green']
            else:
                self.result_label.set_text(f"{best_officer.name} 未搜索到人才")
                self.result_label.color = COLORS['red']
        else:
            self.result_label.set_text("没有武将可以执行此操作")
            self.result_label.color = COLORS['red']

        self._update_city_info()

    def _on_recruit_prisoners(self):
        """招降俘虏"""
        self.result_label.set_text("暂无俘虏")
        self.result_label.color = COLORS['gray']

    def _on_draft_troops(self):
        """征兵"""
        if not self.current_city:
            return

        # 找一个魅力高的武将来征兵
        best_officer = None
        best_chr = 0
        for oid in self.current_city.officer_ids:
            officer = officer_manager.get_officer(oid)
            if officer and officer.attributes.charisma > best_chr:
                best_chr = officer.attributes.charisma
                best_officer = officer

        if best_officer:
            amount = 1000  # 征兵数量
            result = self.current_city.draft_troops(amount, best_officer.attributes.charisma)
            if result > 0:
                self.result_label.set_text(f"{best_officer.name} 成功征兵 {result} 人")
                self.result_label.color = COLORS['green']
            else:
                self.result_label.set_text(f"资源不足或人口不足")
                self.result_label.color = COLORS['red']
        else:
            self.result_label.set_text("没有武将可以执行此操作")
            self.result_label.color = COLORS['red']

        self._update_city_info()

    def _on_march(self):
        """出征"""
        logger.info("出征")
        self.game.change_scene('battle')

    def handle_event(self, event):
        """处理事件"""
        self.ui_root.handle_event(event)

        # 处理武将列表点击
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            for rect, officer_id in self.officer_click_rects:
                if rect.collidepoint(mouse_pos):
                    officer = officer_manager.get_officer(officer_id)
                    if officer:
                        logger.info(f"点击武将: {officer.name}")
                        self.game.change_scene('officer', officer, 'city', self.current_city)
                    break

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
        if not self.current_city:
            return

        # 清空点击区域
        self.officer_click_rects = []

        abs_x, abs_y = self.middle_panel.get_absolute_pos()
        start_y = abs_y + 70

        officers = [officer_manager.get_officer(oid) for oid in self.current_city.officer_ids]
        officers = [o for o in officers if o]  # 过滤掉None

        for i, officer in enumerate(officers):
            y = start_y + i * 50
            if y > abs_y + self.middle_panel.rect.height - 50:
                break

            # 绘制点击区域背景（鼠标悬停效果）
            row_rect = pygame.Rect(abs_x + 10, y - 5, self.middle_panel.rect.width - 20, 45)
            mouse_pos = pygame.mouse.get_pos()
            if row_rect.collidepoint(mouse_pos):
                pygame.draw.rect(screen, (60, 60, 80), row_rect)
            pygame.draw.rect(screen, COLORS['gray'], row_rect, 1)

            # 存储点击区域
            self.officer_click_rects.append((row_rect, officer.id))

            # 武将名称
            name_surface = self.game.get_font('default').render(
                f"{officer.name} {officer.courtesy_name}", True, COLORS['text']
            )
            screen.blit(name_surface, (abs_x + 20, y))

            # 属性
            attr_text = f"武:{officer.attributes.war} 智:{officer.attributes.intelligence} 政:{officer.attributes.politics}"
            attr_surface = self.game.get_font('small').render(attr_text, True, COLORS['gray'])
            screen.blit(attr_surface, (abs_x + 150, y + 5))

            # 忠诚度
            loyalty_text = f"忠:{officer.loyalty}"
            loyalty_surface = self.game.get_font('small').render(loyalty_text, True, COLORS['dark_red'])
            screen.blit(loyalty_surface, (abs_x + 320, y + 5))
