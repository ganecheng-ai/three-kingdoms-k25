"""
三国霸业游戏 - 武将系统
"""

import json
import random
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict
from utils.logger import get_logger

logger = get_logger('officer')


@dataclass
class OfficerAttributes:
    """武将属性"""
    war: int = 50       # 武力
    intelligence: int = 50  # 智力
    politics: int = 50      # 政治
    charisma: int = 50      # 魅力

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(**data)


@dataclass
class Officer:
    """武将数据类"""
    id: int
    name: str                   # 姓名
    courtesy_name: str = ""     # 字
    faction_id: int = 0         # 所属势力ID
    city_id: int = 0            # 所在城池ID
    attributes: OfficerAttributes = None  # 属性
    skills: List[str] = None    # 技能列表
    loyalty: int = 100          # 忠诚度
    troops: int = 0             # 带兵数
    status: str = "idle"        # 状态: idle(空闲), marching(出征), task(任务), prisoner(俘虏)
    health: int = 100           # 健康值
    experience: int = 0         # 经验值
    level: int = 1              # 等级
    age: int = 30               # 年龄

    def __post_init__(self):
        if self.attributes is None:
            self.attributes = OfficerAttributes()
        if self.skills is None:
            self.skills = []

    def to_dict(self) -> dict:
        """转换为字典"""
        data = asdict(self)
        data['attributes'] = self.attributes.to_dict()
        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'Officer':
        """从字典创建"""
        attrs = data.pop('attributes', {})
        officer = cls(**data)
        officer.attributes = OfficerAttributes.from_dict(attrs)
        return officer

    def get_battle_power(self) -> int:
        """计算战斗力"""
        return (self.attributes.war * 2 +
                self.attributes.intelligence +
                self.troops // 100)

    def can_recruit(self, gold_cost: int) -> bool:
        """检查是否可以招募"""
        return self.loyalty > 80 and self.status == "idle"

    def train_troops(self, amount: int, food_cost: int) -> bool:
        """训练士兵"""
        if self.status != "idle":
            return False
        self.troops = min(99999, self.troops + amount)
        return True

    def __str__(self):
        return f"{self.name}({self.courtesy_name}) 武{self.attributes.war}智{self.attributes.intelligence}政{self.attributes.politics}魅{self.attributes.charisma}"


class OfficerManager:
    """武将管理器"""

    def __init__(self):
        self.officers: Dict[int, Officer] = {}
        self._next_id = 1
        self._load_default_officers()

    def _load_default_officers(self):
        """加载默认武将数据"""
        # 魏国武将
        self.add_officer(Officer(
            id=self._get_next_id(),
            name="曹操",
            courtesy_name="孟德",
            faction_id=1,
            attributes=OfficerAttributes(war=72, intelligence=91, politics=94, charisma=96),
            skills=["奸雄", "驱虎吞狼"],
            loyalty=100,
            age=42
        ))
        self.add_officer(Officer(
            id=self._get_next_id(),
            name="司马懿",
            courtesy_name="仲达",
            faction_id=1,
            attributes=OfficerAttributes(war=65, intelligence=98, politics=95, charisma=78),
            skills=["鹰视狼顾", "鬼谋"],
            loyalty=85,
            age=35
        ))
        self.add_officer(Officer(
            id=self._get_next_id(),
            name="张辽",
            courtesy_name="文远",
            faction_id=1,
            attributes=OfficerAttributes(war=92, intelligence=78, politics=65, charisma=82),
            skills=["威震逍遥津"],
            loyalty=95,
            age=38
        ))
        self.add_officer(Officer(
            id=self._get_next_id(),
            name="夏侯惇",
            courtesy_name="元让",
            faction_id=1,
            attributes=OfficerAttributes(war=90, intelligence=65, politics=60, charisma=75),
            skills=["刚烈"],
            loyalty=100,
            age=40
        ))

        # 蜀国武将
        self.add_officer(Officer(
            id=self._get_next_id(),
            name="刘备",
            courtesy_name="玄德",
            faction_id=2,
            attributes=OfficerAttributes(war=75, intelligence=78, politics=80, charisma=99),
            skills=[["仁德", "激将"]],
            loyalty=100,
            age=42
        ))
        self.add_officer(Officer(
            id=self._get_next_id(),
            name="诸葛亮",
            courtesy_name="孔明",
            faction_id=2,
            attributes=OfficerAttributes(war=60, intelligence=100, politics=98, charisma=92),
            skills=["观星", "空城", "火计", "八阵图"],
            loyalty=100,
            age=32
        ))
        self.add_officer(Officer(
            id=self._get_next_id(),
            name="关羽",
            courtesy_name="云长",
            faction_id=2,
            attributes=OfficerAttributes(war=98, intelligence=76, politics=65, charisma=95),
            skills=["武圣", "拖刀"],
            loyalty=100,
            age=40
        ))
        self.add_officer(Officer(
            id=self._get_next_id(),
            name="张飞",
            courtesy_name="翼德",
            faction_id=2,
            attributes=OfficerAttributes(war=99, intelligence=30, politics=35, charisma=70),
            skills=["咆哮", "震慑"],
            loyalty=100,
            age=38
        ))
        self.add_officer(Officer(
            id=self._get_next_id(),
            name="赵云",
            courtesy_name="子龙",
            faction_id=2,
            attributes=OfficerAttributes(war=97, intelligence=76, politics=70, charisma=88),
            skills=["龙胆", "七进七出"],
            loyalty=100,
            age=35
        ))

        # 吴国武将
        self.add_officer(Officer(
            id=self._get_next_id(),
            name="孙权",
            courtesy_name="仲谋",
            faction_id=3,
            attributes=OfficerAttributes(war=70, intelligence=82, politics=88, charisma=90),
            skills=["制衡", "救援"],
            loyalty=100,
            age=35
        ))
        self.add_officer(Officer(
            id=self._get_next_id(),
            name="周瑜",
            courtesy_name="公瑾",
            faction_id=3,
            attributes=OfficerAttributes(war=72, intelligence=97, politics=88, charisma=95),
            skills=[["英姿", "反间", "火攻"]],
            loyalty=95,
            age=33
        ))
        self.add_officer(Officer(
            id=self._get_next_id(),
            name="陆逊",
            courtesy_name="伯言",
            faction_id=3,
            attributes=OfficerAttributes(war=70, intelligence=96, politics=90, charisma=85),
            skills=["连营", "火烧连营"],
            loyalty=95,
            age=30
        ))
        self.add_officer(Officer(
            id=self._get_next_id(),
            name="甘宁",
            courtesy_name="兴霸",
            faction_id=3,
            attributes=OfficerAttributes(war=94, intelligence=78, politics=65, charisma=80),
            skills=[["奇袭", "锦帆"]],
            loyalty=85,
            age=32
        ))

        # 中立武将
        self.add_officer(Officer(
            id=self._get_next_id(),
            name="吕布",
            courtesy_name="奉先",
            faction_id=0,
            attributes=OfficerAttributes(war=100, intelligence=26, politics=30, charisma=65),
            skills=["无双", "飞将"],
            loyalty=50,
            age=35
        ))
        self.add_officer(Officer(
            id=self._get_next_id(),
            name="貂蝉",
            courtesy_name="",
            faction_id=0,
            attributes=OfficerAttributes(war=20, intelligence=85, politics=75, charisma=100),
            skills=[["闭月", "离间"]],
            loyalty=60,
            age=22
        ))

        logger.info(f"加载了 {len(self.officers)} 名武将")

    def _get_next_id(self) -> int:
        """获取下一个ID"""
        id = self._next_id
        self._next_id += 1
        return id

    def add_officer(self, officer: Officer) -> bool:
        """添加武将"""
        if officer.id in self.officers:
            logger.warning(f"武将ID已存在: {officer.id}")
            return False
        self.officers[officer.id] = officer
        return True

    def get_officer(self, officer_id: int) -> Optional[Officer]:
        """获取武将"""
        return self.officers.get(officer_id)

    def get_officers_by_faction(self, faction_id: int) -> List[Officer]:
        """获取势力下的所有武将"""
        return [o for o in self.officers.values() if o.faction_id == faction_id]

    def get_officers_by_city(self, city_id: int) -> List[Officer]:
        """获取城池中的所有武将"""
        return [o for o in self.officers.values() if o.city_id == city_id]

    def get_free_officers(self) -> List[Officer]:
        """获取在野武将（无势力）"""
        return [o for o in self.officers.values() if o.faction_id == 0]

    def search_officers(self, city_id: int, success_rate: float = 0.3) -> Optional[Officer]:
        """在城池中搜索人才"""
        # 简单实现：随机决定是否找到武将
        if random.random() > success_rate:
            return None

        # 找到在野或未归属该城的武将
        candidates = [o for o in self.officers.values()
                     if o.faction_id == 0 or (o.city_id == 0 and o.faction_id != 0)]

        if candidates:
            found = random.choice(candidates)
            found.city_id = city_id
            logger.info(f"搜索到武将: {found.name}")
            return found
        return None

    def recruit_officer(self, officer_id: int, faction_id: int, cost: int = 1000) -> bool:
        """招募武将"""
        officer = self.get_officer(officer_id)
        if not officer:
            return False

        if officer.faction_id == faction_id:
            return True  # 已经是自己人了

        # 检查忠诚度
        if officer.loyalty > 80 and officer.faction_id != 0:
            logger.info(f"{officer.name} 忠诚度太高，无法招募")
            return False

        officer.faction_id = faction_id
        officer.loyalty = min(100, officer.loyalty + 20)
        logger.info(f"成功招募武将: {officer.name}")
        return True

    def save_to_file(self, filepath: str):
        """保存到文件"""
        data = {oid: officer.to_dict() for oid, officer in self.officers.items()}
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"武将数据已保存到: {filepath}")

    def load_from_file(self, filepath: str):
        """从文件加载"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.officers.clear()
            for oid, odata in data.items():
                officer = Officer.from_dict(odata)
                self.officers[int(oid)] = officer

            # 更新_next_id
            if self.officers:
                self._next_id = max(self.officers.keys()) + 1

            logger.info(f"从 {filepath} 加载了 {len(self.officers)} 名武将")
        except Exception as e:
            logger.error(f"加载武将数据失败: {e}")


# 全局武将管理器实例
officer_manager = OfficerManager()
