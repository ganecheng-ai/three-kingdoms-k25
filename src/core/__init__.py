"""
三国霸业游戏 - 核心模块
"""

from .officer import Officer, OfficerAttributes, OfficerManager, officer_manager
from .city import City, CityResources, CityManager, city_manager
from .faction import Faction, FactionType, FactionManager, faction_manager, FACTION_NAMES
from .save_manager import SaveSlot, SaveManager, save_manager

__all__ = [
    'Officer', 'OfficerAttributes', 'OfficerManager', 'officer_manager',
    'City', 'CityResources', 'CityManager', 'city_manager',
    'Faction', 'FactionType', 'FactionManager', 'faction_manager', 'FACTION_NAMES',
    'SaveSlot', 'SaveManager', 'save_manager',
]
