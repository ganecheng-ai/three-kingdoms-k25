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
from scenes.officer import OfficerScene
from scenes.diplomacy import DiplomacyScene
from core.officer import officer_manager
from core.city import city_manager
from core.faction import faction_manager
from core.save_manager import save_manager

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

        # 游戏数据管理器
        self.officer_manager = officer_manager
        self.city_manager = city_manager
        self.faction_manager = faction_manager
        self.save_manager = save_manager

        # 游戏状态
        self.current_turn = 1
        self.current_date = (184, 1)  # (年份, 月份)
        self.selected_city = None

        # 初始化游戏数据
        self._init_game_data()

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
        self.scenes['officer'] = OfficerScene(self)
        self.scenes['diplomacy'] = DiplomacyScene(self)

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

    def _init_game_data(self):
        """初始化游戏数据"""
        logger.info("初始化游戏数据...")

        # 关联武将和城池
        self._link_officers_to_cities()

        # 关联城池和势力
        self._link_cities_to_factions()

        # 更新势力资源
        self.faction_manager.update_all_resources(self.city_manager.cities)

        logger.info("游戏数据初始化完成")

    def _link_officers_to_cities(self):
        """关联武将与城池"""
        # 为每个武将分配城池
        for officer in self.officer_manager.officers.values():
            if officer.faction_id > 0:
                # 获取势力下的城池
                faction_cities = self.city_manager.get_cities_by_faction(officer.faction_id)
                if faction_cities:
                    # 将武将放入势力的第一个城池
                    city = faction_cities[0]
                    officer.city_id = city.id
                    city.add_officer(officer.id)

    def _link_cities_to_factions(self):
        """关联城池与势力"""
        for city in self.city_manager.cities.values():
            if city.faction_id > 0:
                faction = self.faction_manager.get_faction(city.faction_id)
                if faction:
                    faction.add_city(city.id)

    def get_formatted_date(self) -> str:
        """获取格式化日期"""
        year, month = self.current_date
        return f"公元 {year}年 {month}月"

    def next_turn(self):
        """进入下一回合"""
        self.current_turn += 1

        # 更新日期
        year, month = self.current_date
        month += 1
        if month > 12:
            month = 1
            year += 1
        self.current_date = (year, month)

        # 处理回合更新
        self._process_turn_update()

        logger.info(f"进入第 {self.current_turn} 回合: {self.get_formatted_date()}")

    def _process_turn_update(self):
        """处理回合更新"""
        # 更新所有城池
        self.city_manager.process_turn()

        # 更新势力资源
        self.faction_manager.update_all_resources(self.city_manager.cities)

        # 自动存档
        if config.get('game.auto_save'):
            self.auto_save()

    def select_city(self, city_id: int):
        """选择城池"""
        self.selected_city = self.city_manager.get_city(city_id)
        return self.selected_city

    def new_game(self, player_faction_id: int = 2):
        """开始新游戏"""
        logger.info(f"开始新游戏，玩家势力: {player_faction_id}")

        self.current_turn = 1
        self.current_date = (184, 1)
        self.selected_city = None

        # 设置玩家势力
        self.faction_manager.set_player_faction(player_faction_id)

        # 重新初始化数据
        self._init_game_data()

        # 切换到大地图
        self.change_scene('world_map')

    def save_game(self, slot_id: int, name: str = "") -> bool:
        """保存游戏"""
        game_data = {
            'turn': self.current_turn,
            'date': self.current_date,
            'player_faction_id': self.faction_manager.player_faction_id,
            'player_faction_name': self.faction_manager.get_player_faction().name if self.faction_manager.get_player_faction() else "",
            'cities': {cid: city.to_dict() for cid, city in self.city_manager.cities.items()},
            'officers': {oid: officer.to_dict() for oid, officer in self.officer_manager.officers.items()},
            'factions': {fid: faction.to_dict() for fid, faction in self.faction_manager.factions.items()},
        }
        return self.save_manager.save_game(slot_id, game_data, name)

    def load_game(self, slot_id: int) -> bool:
        """加载游戏"""
        game_data = self.save_manager.load_game(slot_id)
        if not game_data:
            return False

        try:
            # 恢复游戏状态
            self.current_turn = game_data.get('turn', 1)
            self.current_date = tuple(game_data.get('date', [184, 1]))

            # 恢复势力数据
            self.faction_manager.factions.clear()
            for fid, fdata in game_data['factions'].items():
                from core.faction import Faction
                self.faction_manager.factions[int(fid)] = Faction.from_dict(fdata)
            self.faction_manager.player_faction_id = game_data.get('player_faction_id', 2)

            # 恢复城池数据
            self.city_manager.cities.clear()
            for cid, cdata in game_data['cities'].items():
                from core.city import City
                self.city_manager.cities[int(cid)] = City.from_dict(cdata)

            # 恢复武将数据
            self.officer_manager.officers.clear()
            for oid, odata in game_data['officers'].items():
                from core.officer import Officer
                self.officer_manager.officers[int(oid)] = Officer.from_dict(odata)

            logger.info(f"游戏加载成功，当前回合: {self.current_turn}")
            return True

        except Exception as e:
            logger.error(f"加载游戏数据失败: {e}")
            return False

    def auto_save(self) -> bool:
        """自动存档"""
        return self.save_game(0, "自动存档")

    def get_player_faction(self):
        """获取玩家势力"""
        return self.faction_manager.get_player_faction()

    def get_player_cities(self):
        """获取玩家城池"""
        faction = self.get_player_faction()
        if faction:
            return [self.city_manager.get_city(cid) for cid in faction.city_ids]
        return []

    def quit(self):
        """退出游戏"""
        logger.info("游戏退出中...")

        # 通知所有场景退出
        for scene in self.scenes.values():
            scene.on_exit()

        pygame.quit()
        sys.exit(0)
