"""
三国霸业游戏 - 基础场景类
"""

from utils.logger import get_logger

logger = get_logger('scene')


class BaseScene:
    """场景基类"""

    def __init__(self, game):
        """初始化场景"""
        self.game = game
        self.name = 'base'
        self.initialized = False
        logger.debug(f"场景初始化: {self.__class__.__name__}")

    def on_enter(self, *args, **kwargs):
        """进入场景时调用"""
        logger.debug(f"进入场景: {self.__class__.__name__}")
        if not self.initialized:
            self._init_scene()
            self.initialized = True

    def on_exit(self):
        """退出场景时调用"""
        logger.debug(f"退出场景: {self.__class__.__name__}")

    def _init_scene(self):
        """初始化场景内容（子类重写）"""
        pass

    def handle_event(self, event):
        """处理事件（子类重写）"""
        pass

    def update(self, dt):
        """更新场景（子类重写）"""
        pass

    def render(self, screen):
        """渲染场景（子类重写）"""
        pass
