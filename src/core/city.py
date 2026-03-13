"""
三国霸业游戏 - 城池系统
"""

import json
import random
from dataclasses import dataclass, asdict, field
from typing import List, Optional, Dict, Set
from utils.logger import get_logger

logger = get_logger('city')


@dataclass
class CityResources:
    """城池资源"""
    gold: int = 10000       # 金钱
    food: int = 50000       # 粮草

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(**data)


@dataclass
class City:
    """城池数据类"""
    id: int
    name: str                   # 城池名
    faction_id: int = 0         # 所属势力ID
    population: int = 10000     # 人口
    agriculture: int = 50       # 农业 (0-100)
    commerce: int = 50          # 商业 (0-100)
    defense: int = 50           # 城防 (0-100)
    governor_id: int = 0        # 太守ID
    officer_ids: List[int] = field(default_factory=list)  # 城中武将ID列表
    troops: int = 5000          # 兵力
    resources: CityResources = field(default_factory=CityResources)
    x: int = 0                  # 地图X坐标
    y: int = 0                  # 地图Y坐标
    adjacent_cities: List[int] = field(default_factory=list)  # 相邻城池

    def __post_init__(self):
        if isinstance(self.resources, dict):
            self.resources = CityResources(**self.resources)

    def to_dict(self) -> dict:
        """转换为字典"""
        data = asdict(self)
        data['resources'] = self.resources.to_dict()
        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'City':
        """从字典创建"""
        resources = data.pop('resources', {})
        city = cls(**data)
        city.resources = CityResources.from_dict(resources)
        return city

    def get_monthly_income(self) -> tuple:
        """计算月度收入 (金钱, 粮草)"""
        gold_income = int(self.population * 0.1 * (self.commerce / 100))
        food_income = int(self.population * 0.5 * (self.agriculture / 100))
        return gold_income, food_income

    def get_monthly_consumption(self) -> tuple:
        """计算月度消耗 (金钱, 粮草)"""
        gold_cost = int(self.troops * 0.5 + self.population * 0.02)
        food_cost = int(self.troops * 2)
        return gold_cost, food_cost

    def develop_agriculture(self, officer_int: int, officer_pol: int) -> int:
        """开发农业"""
        if self.agriculture >= 100:
            return 0

        # 成功率基于智力和政治
        success_rate = min(0.9, (officer_int + officer_pol) / 200)
        if random.random() > success_rate:
            return 0

        # 增加量
        increase = random.randint(3, 8)
        old_val = self.agriculture
        self.agriculture = min(100, self.agriculture + increase)
        actual_increase = self.agriculture - old_val

        # 消耗金钱
        cost = 500
        self.resources.gold = max(0, self.resources.gold - cost)

        logger.info(f"{self.name} 农业开发: {actual_increase}, 当前: {self.agriculture}")
        return actual_increase

    def develop_commerce(self, officer_int: int, officer_pol: int) -> int:
        """发展商业"""
        if self.commerce >= 100:
            return 0

        success_rate = min(0.9, (officer_int + officer_pol) / 200)
        if random.random() > success_rate:
            return 0

        increase = random.randint(3, 8)
        old_val = self.commerce
        self.commerce = min(100, self.commerce + increase)
        actual_increase = self.commerce - old_val

        cost = 500
        self.resources.gold = max(0, self.resources.gold - cost)

        logger.info(f"{self.name} 商业发展: {actual_increase}, 当前: {self.commerce}")
        return actual_increase

    def develop_defense(self, officer_int: int, officer_pol: int) -> int:
        """加强城防"""
        if self.defense >= 100:
            return 0

        success_rate = min(0.9, (officer_int + officer_pol) / 200)
        if random.random() > success_rate:
            return 0

        increase = random.randint(2, 6)
        old_val = self.defense
        self.defense = min(100, self.defense + increase)
        actual_increase = self.defense - old_val

        cost = 800
        self.resources.gold = max(0, self.resources.gold - cost)

        logger.info(f"{self.name} 城防加强: {actual_increase}, 当前: {self.defense}")
        return actual_increase

    def draft_troops(self, amount: int, officer_chr: int) -> int:
        """征兵"""
        # 基于魅力影响征兵效率
        max_troops = int(self.population * 0.1 * (0.5 + officer_chr / 200))
        actual_amount = min(amount, max_troops)

        if actual_amount <= 0:
            return 0

        # 消耗金钱和粮草
        gold_cost = actual_amount * 10
        food_cost = actual_amount * 5

        if self.resources.gold < gold_cost or self.resources.food < food_cost:
            return 0

        self.resources.gold -= gold_cost
        self.resources.food -= food_cost
        self.troops += actual_amount

        logger.info(f"{self.name} 征兵: {actual_amount}, 总兵力: {self.troops}")
        return actual_amount

    def move_troops(self, amount: int, target_city_id: int) -> bool:
        """调动兵力到其他城池"""
        if amount > self.troops:
            return False

        self.troops -= amount
        logger.info(f"{self.name} 调出 {amount} 兵力到城池 {target_city_id}")
        return True

    def receive_troops(self, amount: int):
        """接收调动来的兵力"""
        self.troops += amount

    def add_officer(self, officer_id: int):
        """添加武将到城池"""
        if officer_id not in self.officer_ids:
            self.officer_ids.append(officer_id)

    def remove_officer(self, officer_id: int):
        """从城池移除武将"""
        if officer_id in self.officer_ids:
            self.officer_ids.remove(officer_id)

    def process_turn(self):
        """处理回合更新"""
        # 收入
        gold_income, food_income = self.get_monthly_income()
        # 消耗
        gold_cost, food_cost = self.get_monthly_consumption()

        self.resources.gold += gold_income - gold_cost
        self.resources.food += food_income - food_cost

        # 人口自然增长
        growth = int(self.population * 0.001)
        self.population += growth

        # 确保资源不为负
        self.resources.gold = max(0, self.resources.gold)
        self.resources.food = max(0, self.resources.food)

    def __str__(self):
        return f"{self.name}(人口:{self.population} 农业:{self.agriculture} 商业:{self.commerce} 兵力:{self.troops})"


class CityManager:
    """城池管理器"""

    def __init__(self):
        self.cities: Dict[int, City] = {}
        self._next_id = 1
        self._load_default_cities()

    def _load_default_cities(self):
        """加载默认城池数据"""
        cities_data = [
            # 魏国城池
            {"name": "许昌", "faction_id": 1, "x": 800, "y": 500, "population": 80000},
            {"name": "洛阳", "faction_id": 1, "x": 650, "y": 480, "population": 100000},
            {"name": "邺城", "faction_id": 1, "x": 850, "y": 350, "population": 70000},
            {"name": "陈留", "faction_id": 1, "x": 900, "y": 520, "population": 60000},
            {"name": "长安", "faction_id": 1, "x": 500, "y": 500, "population": 80000},
            {"name": "小沛", "faction_id": 1, "x": 950, "y": 550, "population": 40000},

            # 蜀国城池
            {"name": "成都", "faction_id": 2, "x": 350, "y": 650, "population": 90000},
            {"name": "汉中", "faction_id": 2, "x": 480, "y": 550, "population": 50000},
            {"name": "江州", "faction_id": 2, "x": 450, "y": 700, "population": 45000},
            {"name": "永安", "faction_id": 2, "x": 600, "y": 680, "population": 40000},

            # 吴国城池
            {"name": "建业", "faction_id": 3, "x": 1100, "y": 650, "population": 85000},
            {"name": "吴郡", "faction_id": 3, "x": 1150, "y": 600, "population": 60000},
            {"name": "柴桑", "faction_id": 3, "x": 1000, "y": 750, "population": 50000},
            {"name": "长沙", "faction_id": 3, "x": 850, "y": 800, "population": 55000},
            {"name": "襄阳", "faction_id": 3, "x": 750, "y": 620, "population": 70000},

            # 中立/其他城池
            {"name": "北平", "faction_id": 0, "x": 1000, "y": 250, "population": 45000},
            {"name": "南皮", "faction_id": 0, "x": 950, "y": 300, "population": 40000},
            {"name": "下邳", "faction_id": 0, "x": 1000, "y": 500, "population": 50000},
            {"name": "寿春", "faction_id": 0, "x": 1050, "y": 580, "population": 60000},
            {"name": "宛城", "faction_id": 0, "x": 750, "y": 550, "population": 45000},
            {"name": "新野", "faction_id": 0, "x": 700, "y": 600, "population": 35000},
            {"name": "武陵", "faction_id": 0, "x": 700, "y": 750, "population": 40000},
            {"name": "桂阳", "faction_id": 0, "x": 800, "y": 850, "population": 35000},
            {"name": "零陵", "faction_id": 0, "x": 750, "y": 820, "population": 35000},
            {"name": "云南", "faction_id": 0, "x": 400, "y": 850, "population": 30000},
        ]

        # 创建城池
        for data in cities_data:
            city = City(
                id=self._get_next_id(),
                name=data["name"],
                faction_id=data["faction_id"],
                x=data["x"],
                y=data["y"],
                population=data["population"],
                resources=CityResources(
                    gold=random.randint(5000, 15000),
                    food=random.randint(30000, 80000)
                ),
                troops=random.randint(3000, 8000)
            )
            self.add_city(city)

        # 设置相邻城池
        self._setup_adjacent_cities()

        logger.info(f"加载了 {len(self.cities)} 座城池")

    def _setup_adjacent_cities(self):
        """设置相邻城池关系"""
        # 基于距离设置相邻关系
        for city in self.cities.values():
            adjacent = []
            for other in self.cities.values():
                if city.id == other.id:
                    continue
                distance = ((city.x - other.x) ** 2 + (city.y - other.y) ** 2) ** 0.5
                if distance < 200:  # 距离小于200像素视为相邻
                    adjacent.append(other.id)
            city.adjacent_cities = adjacent

    def _get_next_id(self) -> int:
        """获取下一个ID"""
        id = self._next_id
        self._next_id += 1
        return id

    def add_city(self, city: City) -> bool:
        """添加城池"""
        if city.id in self.cities:
            logger.warning(f"城池ID已存在: {city.id}")
            return False
        self.cities[city.id] = city
        return True

    def get_city(self, city_id: int) -> Optional[City]:
        """获取城池"""
        return self.cities.get(city_id)

    def get_city_by_name(self, name: str) -> Optional[City]:
        """通过名称获取城池"""
        for city in self.cities.values():
            if city.name == name:
                return city
        return None

    def get_cities_by_faction(self, faction_id: int) -> List[City]:
        """获取势力下的所有城池"""
        return [c for c in self.cities.values() if c.faction_id == faction_id]

    def get_adjacent_cities(self, city_id: int) -> List[City]:
        """获取相邻城池"""
        city = self.get_city(city_id)
        if not city:
            return []
        return [self.get_city(cid) for cid in city.adjacent_cities if self.get_city(cid)]

    def get_enemy_adjacent_cities(self, city_id: int) -> List[City]:
        """获取相邻的敌方城池"""
        city = self.get_city(city_id)
        if not city:
            return []
        return [c for c in self.get_adjacent_cities(city_id) if c.faction_id != city.faction_id]

    def change_faction(self, city_id: int, new_faction_id: int) -> bool:
        """改变城池归属"""
        city = self.get_city(city_id)
        if not city:
            return False

        old_faction = city.faction_id
        city.faction_id = new_faction_id

        # 城中武将也改变归属
        for officer_id in city.officer_ids:
            logger.info(f"武将 {officer_id} 归属变更为势力 {new_faction_id}")

        logger.info(f"城池 {city.name} 归属变更: {old_faction} -> {new_faction_id}")
        return True

    def process_turn(self):
        """处理所有城池的回合更新"""
        for city in self.cities.values():
            city.process_turn()

    def save_to_file(self, filepath: str):
        """保存到文件"""
        data = {cid: city.to_dict() for cid, city in self.cities.items()}
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"城池数据已保存到: {filepath}")

    def load_from_file(self, filepath: str):
        """从文件加载"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.cities.clear()
            for cid, cdata in data.items():
                city = City.from_dict(cdata)
                self.cities[int(cid)] = city

            if self.cities:
                self._next_id = max(self.cities.keys()) + 1

            logger.info(f"从 {filepath} 加载了 {len(self.cities)} 座城池")
        except Exception as e:
            logger.error(f"加载城池数据失败: {e}")


# 全局城池管理器实例
city_manager = CityManager()
