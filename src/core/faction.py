"""
三国霸业游戏 - 势力系统
"""

import json
from dataclasses import dataclass, asdict, field
from typing import List, Optional, Dict
from enum import Enum
from utils.logger import get_logger

logger = get_logger('faction')


class FactionType(Enum):
    """势力类型"""
    NEUTRAL = 0     # 中立
    WEI = 1         # 魏
    SHU = 2         # 蜀
    WU = 3          # 吴
    YELLOW_TURBAN = 4  # 黄巾
    DONG_ZHUO = 5   # 董卓
    YUAN_SHAO = 6   # 袁绍
    OTHER = 7       # 其他


FACTION_NAMES = {
    0: "中立",
    1: "魏",
    2: "蜀",
    3: "吴",
    4: "黄巾",
    5: "董卓",
    6: "袁绍",
    7: "其他"
}


@dataclass
class Faction:
    """势力数据类"""
    id: int
    name: str                   # 势力名
    leader_id: int = 0          # 君主ID
    color: tuple = (128, 128, 128)  # 势力颜色 (R, G, B)
    city_ids: List[int] = field(default_factory=list)  # 城池ID列表
    officer_ids: List[int] = field(default_factory=list)  # 武将ID列表
    total_gold: int = 0         # 总金钱
    total_food: int = 0         # 总粮草
    total_troops: int = 0       # 总兵力
    diplomacy: Dict[int, int] = field(default_factory=dict)  # 外交关系 {faction_id: relation}
    player_controlled: bool = False  # 是否玩家控制

    def to_dict(self) -> dict:
        """转换为字典"""
        data = asdict(self)
        data['color'] = list(self.color)  # tuple转list以便JSON序列化
        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'Faction':
        """从字典创建"""
        color = data.pop('color', [128, 128, 128])
        faction = cls(**data)
        faction.color = tuple(color) if isinstance(color, list) else color
        return faction

    def update_resources(self, cities: dict):
        """更新资源统计"""
        self.total_gold = 0
        self.total_food = 0
        self.total_troops = 0

        for city_id in self.city_ids:
            if city_id in cities:
                city = cities[city_id]
                self.total_gold += city.resources.gold
                self.total_food += city.resources.food
                self.total_troops += city.troops

    def get_diplomatic_relation(self, other_faction_id: int) -> int:
        """获取外交关系值 (-100到100)"""
        return self.diplomacy.get(other_faction_id, 0)

    def set_diplomatic_relation(self, other_faction_id: int, value: int):
        """设置外交关系"""
        self.diplomacy[other_faction_id] = max(-100, min(100, value))

    def is_at_war(self, other_faction_id: int) -> bool:
        """检查是否处于战争状态"""
        return self.get_diplomatic_relation(other_faction_id) < -50

    def is_allied(self, other_faction_id: int) -> bool:
        """检查是否结盟"""
        return self.get_diplomatic_relation(other_faction_id) > 50

    def add_city(self, city_id: int):
        """添加城池"""
        if city_id not in self.city_ids:
            self.city_ids.append(city_id)

    def remove_city(self, city_id: int):
        """移除城池"""
        if city_id in self.city_ids:
            self.city_ids.remove(city_id)

    def add_officer(self, officer_id: int):
        """添加武将"""
        if officer_id not in self.officer_ids:
            self.officer_ids.append(officer_id)

    def remove_officer(self, officer_id: int):
        """移除武将"""
        if officer_id in self.officer_ids:
            self.officer_ids.remove(officer_id)

    def get_power_score(self) -> int:
        """计算势力评分"""
        city_score = len(self.city_ids) * 1000
        troop_score = self.total_troops
        resource_score = (self.total_gold + self.total_food // 10) // 100
        return city_score + troop_score + resource_score

    def __str__(self):
        return f"{self.name}(城池:{len(self.city_ids)} 兵力:{self.total_troops})"


class FactionManager:
    """势力管理器"""

    def __init__(self):
        self.factions: Dict[int, Faction] = {}
        self.player_faction_id: int = 2  # 默认玩家控制蜀国
        self._load_default_factions()

    def _load_default_factions(self):
        """加载默认势力数据"""
        factions_data = [
            {
                "id": 0,
                "name": "中立",
                "color": (128, 128, 128),
                "player_controlled": False
            },
            {
                "id": 1,
                "name": "魏",
                "leader_id": 1,  # 曹操
                "color": (255, 0, 0),
                "player_controlled": False
            },
            {
                "id": 2,
                "name": "蜀",
                "leader_id": 5,  # 刘备
                "color": (0, 200, 0),
                "player_controlled": True
            },
            {
                "id": 3,
                "name": "吴",
                "leader_id": 9,  # 孙权
                "color": (0, 100, 255),
                "player_controlled": False
            },
            {
                "id": 4,
                "name": "黄巾",
                "color": (255, 255, 0),
                "player_controlled": False
            },
            {
                "id": 5,
                "name": "董卓",
                "color": (128, 0, 128),
                "player_controlled": False
            },
            {
                "id": 6,
                "name": "袁绍",
                "color": (255, 165, 0),
                "player_controlled": False
            },
        ]

        for data in factions_data:
            faction = Faction(**data)
            self.factions[faction.id] = faction

        logger.info(f"加载了 {len(self.factions)} 个势力")

    def get_faction(self, faction_id: int) -> Optional[Faction]:
        """获取势力"""
        return self.factions.get(faction_id)

    def get_player_faction(self) -> Optional[Faction]:
        """获取玩家势力"""
        return self.factions.get(self.player_faction_id)

    def set_player_faction(self, faction_id: int):
        """设置玩家控制的势力"""
        # 先清除之前的玩家控制
        for faction in self.factions.values():
            faction.player_controlled = False

        # 设置新的玩家势力
        faction = self.factions.get(faction_id)
        if faction:
            faction.player_controlled = True
            self.player_faction_id = faction_id
            logger.info(f"玩家选择势力: {faction.name}")

    def get_all_factions(self) -> List[Faction]:
        """获取所有势力"""
        return list(self.factions.values())

    def get_ai_factions(self) -> List[Faction]:
        """获取所有AI势力"""
        return [f for f in self.factions.values() if not f.player_controlled and f.id != 0]

    def get_faction_ranking(self) -> List[tuple]:
        """获取势力排名 (势力ID, 评分)"""
        rankings = []
        for faction in self.factions.values():
            if faction.id != 0:  # 排除中立
                score = faction.get_power_score()
                rankings.append((faction.id, score))
        rankings.sort(key=lambda x: x[1], reverse=True)
        return rankings

    def update_all_resources(self, cities: dict):
        """更新所有势力的资源统计"""
        for faction in self.factions.values():
            faction.update_resources(cities)

    def check_victory_condition(self) -> Optional[int]:
        """检查胜利条件，返回胜利势力ID"""
        # 简单条件：某个势力占领所有非中立城池
        for faction in self.factions.values():
            if faction.id == 0:
                continue
            if len(faction.city_ids) >= 15:  # 假设总共有约20座城池
                return faction.id
        return None

    def form_alliance(self, faction_id1: int, faction_id2: int) -> bool:
        """建立同盟"""
        f1 = self.factions.get(faction_id1)
        f2 = self.factions.get(faction_id2)

        if not f1 or not f2:
            return False

        f1.set_diplomatic_relation(faction_id2, 70)
        f2.set_diplomatic_relation(faction_id1, 70)

        logger.info(f"{f1.name} 与 {f2.name} 建立同盟")
        return True

    def declare_war(self, faction_id1: int, faction_id2: int) -> bool:
        """宣战"""
        f1 = self.factions.get(faction_id1)
        f2 = self.factions.get(faction_id2)

        if not f1 or not f2:
            return False

        f1.set_diplomatic_relation(faction_id2, -80)
        f2.set_diplomatic_relation(faction_id1, -80)

        logger.info(f"{f1.name} 向 {f2.name} 宣战")
        return True

    def improve_relation(self, faction_id1: int, faction_id2: int, amount: int = 10) -> bool:
        """改善关系"""
        f1 = self.factions.get(faction_id1)
        if not f1:
            return False

        current = f1.get_diplomatic_relation(faction_id2)
        f1.set_diplomatic_relation(faction_id2, current + amount)

        # 双向改善
        f2 = self.factions.get(faction_id2)
        if f2:
            current2 = f2.get_diplomatic_relation(faction_id1)
            f2.set_diplomatic_relation(faction_id1, current2 + amount)

        return True

    def save_to_file(self, filepath: str):
        """保存到文件"""
        data = {
            'factions': {fid: faction.to_dict() for fid, faction in self.factions.items()},
            'player_faction_id': self.player_faction_id
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"势力数据已保存到: {filepath}")

    def load_from_file(self, filepath: str):
        """从文件加载"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.factions.clear()
            for fid, fdata in data['factions'].items():
                faction = Faction.from_dict(fdata)
                self.factions[int(fid)] = faction

            self.player_faction_id = data.get('player_faction_id', 2)

            logger.info(f"从 {filepath} 加载了 {len(self.factions)} 个势力")
        except Exception as e:
            logger.error(f"加载势力数据失败: {e}")


# 全局势力管理器实例
faction_manager = FactionManager()
