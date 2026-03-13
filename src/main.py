"""
三国霸业游戏 - 主入口
"""

import sys
import os

# 添加src到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.game import Game
from utils.logger import get_logger

logger = get_logger('main')


def main():
    """游戏主入口"""
    logger.info("=" * 50)
    logger.info("三国霸业游戏启动")
    logger.info("=" * 50)

    try:
        game = Game()
        game.run()
    except Exception as e:
        logger.exception("游戏运行出错")
        raise
    finally:
        logger.info("游戏结束")


if __name__ == '__main__':
    main()
