"""
三国霸业游戏 - 存档管理器
"""

import json
import os
import pickle
import gzip
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict
from utils.logger import get_logger

logger = get_logger('save_manager')


class SaveSlot:
    """存档槽位"""

    def __init__(self, slot_id: int, name: str = "", timestamp: datetime = None,
                 turn: int = 0, faction_name: str = "", thumbnail_path: str = ""):
        self.slot_id = slot_id
        self.name = name or f"存档 {slot_id}"
        self.timestamp = timestamp or datetime.now()
        self.turn = turn
        self.faction_name = faction_name
        self.thumbnail_path = thumbnail_path

    def to_dict(self) -> dict:
        return {
            'slot_id': self.slot_id,
            'name': self.name,
            'timestamp': self.timestamp.isoformat(),
            'turn': self.turn,
            'faction_name': self.faction_name,
            'thumbnail_path': self.thumbnail_path
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'SaveSlot':
        return cls(
            slot_id=data['slot_id'],
            name=data['name'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            turn=data.get('turn', 0),
            faction_name=data.get('faction_name', ''),
            thumbnail_path=data.get('thumbnail_path', '')
        )

    def get_formatted_time(self) -> str:
        """获取格式化的时间"""
        return self.timestamp.strftime("%Y-%m-%d %H:%M")


class SaveManager:
    """存档管理器"""

    SAVE_DIR = 'saves'
    MAX_SLOTS = 10

    def __init__(self):
        self.save_dir = self._get_save_dir()
        self._ensure_save_dir()
        self.slots: Dict[int, SaveSlot] = {}
        self._scan_existing_saves()

    def _get_save_dir(self) -> str:
        """获取存档目录"""
        base_dir = Path(__file__).parent.parent.parent
        return str(base_dir / self.SAVE_DIR)

    def _ensure_save_dir(self):
        """确保存档目录存在"""
        if not os.path.exists(self.save_dir):
            try:
                os.makedirs(self.save_dir)
                logger.info(f"创建存档目录: {self.save_dir}")
            except Exception as e:
                logger.error(f"创建存档目录失败: {e}")

    def _scan_existing_saves(self):
        """扫描现有存档"""
        for i in range(1, self.MAX_SLOTS + 1):
            slot_file = os.path.join(self.save_dir, f"slot_{i}.json")
            if os.path.exists(slot_file):
                try:
                    with open(slot_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    self.slots[i] = SaveSlot.from_dict(data)
                except Exception as e:
                    logger.error(f"读取存档槽位 {i} 失败: {e}")

    def get_save_path(self, slot_id: int) -> str:
        """获取存档文件路径"""
        return os.path.join(self.save_dir, f"save_{slot_id}.dat")

    def get_slot_info_path(self, slot_id: int) -> str:
        """获取存档信息文件路径"""
        return os.path.join(self.save_dir, f"slot_{slot_id}.json")

    def get_all_slots(self) -> List[SaveSlot]:
        """获取所有存档槽位"""
        return [self.slots.get(i) for i in range(1, self.MAX_SLOTS + 1)]

    def get_save_list(self) -> List[SaveSlot]:
        """获取存档列表（与 get_all_slots 相同，用于兼容）"""
        return self.get_all_slots()

    def get_slot(self, slot_id: int) -> Optional[SaveSlot]:
        """获取指定槽位"""
        return self.slots.get(slot_id)

    def is_slot_used(self, slot_id: int) -> bool:
        """检查槽位是否已使用"""
        return slot_id in self.slots

    def save_game(self, slot_id: int, game_data: dict, name: str = "") -> bool:
        """保存游戏"""
        try:
            save_path = self.get_save_path(slot_id)

            # 压缩保存数据
            with gzip.open(save_path, 'wb') as f:
                pickle.dump(game_data, f)

            # 更新存档信息
            slot = SaveSlot(
                slot_id=slot_id,
                name=name or f"存档 {slot_id}",
                timestamp=datetime.now(),
                turn=game_data.get('turn', 0),
                faction_name=game_data.get('player_faction_name', '')
            )
            self.slots[slot_id] = slot

            # 保存槽位信息
            info_path = self.get_slot_info_path(slot_id)
            with open(info_path, 'w', encoding='utf-8') as f:
                json.dump(slot.to_dict(), f, ensure_ascii=False, indent=2)

            logger.info(f"游戏已保存到槽位 {slot_id}: {slot.name}")
            return True

        except Exception as e:
            logger.error(f"保存游戏失败: {e}")
            return False

    def load_game(self, slot_id: int) -> Optional[dict]:
        """加载游戏"""
        try:
            save_path = self.get_save_path(slot_id)

            if not os.path.exists(save_path):
                logger.warning(f"存档文件不存在: {save_path}")
                return None

            with gzip.open(save_path, 'rb') as f:
                game_data = pickle.load(f)

            logger.info(f"从槽位 {slot_id} 加载游戏成功")
            return game_data

        except Exception as e:
            logger.error(f"加载游戏失败: {e}")
            return None

    def delete_save(self, slot_id: int) -> bool:
        """删除存档"""
        try:
            save_path = self.get_save_path(slot_id)
            info_path = self.get_slot_info_path(slot_id)

            if os.path.exists(save_path):
                os.remove(save_path)
            if os.path.exists(info_path):
                os.remove(info_path)

            if slot_id in self.slots:
                del self.slots[slot_id]

            logger.info(f"删除存档槽位 {slot_id}")
            return True

        except Exception as e:
            logger.error(f"删除存档失败: {e}")
            return False

    def get_first_empty_slot(self) -> int:
        """获取第一个空槽位"""
        for i in range(1, self.MAX_SLOTS + 1):
            if i not in self.slots:
                return i
        return 0

    def auto_save(self, game_data: dict) -> bool:
        """自动存档"""
        return self.save_game(0, game_data, "自动存档")

    def load_auto_save(self) -> Optional[dict]:
        """加载自动存档"""
        return self.load_game(0)

    def has_auto_save(self) -> bool:
        """检查是否有自动存档"""
        return os.path.exists(self.get_save_path(0))


# 全局存档管理器实例
save_manager = SaveManager()
