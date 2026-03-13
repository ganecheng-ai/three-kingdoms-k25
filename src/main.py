"""
三国霸业游戏 - 主入口
"""

import sys
import os

# 检测是否在 PyInstaller 打包环境中运行
if getattr(sys, 'frozen', False):
    # 如果是打包后的环境，使用可执行文件所在目录
    bundle_dir = sys._MEIPASS if hasattr(sys, '_MEIPASS') else os.path.dirname(sys.executable)
    sys.path.insert(0, bundle_dir)
else:
    # 开发环境：添加 src 到路径
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
