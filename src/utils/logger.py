"""
三国霸业游戏 - 日志系统
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# 日志格式
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# 日志级别
LOG_LEVEL = logging.DEBUG

# 单例日志管理器
_logger_manager = None


class LoggerManager:
    """日志管理器 - 管理所有日志记录器"""

    def __init__(self):
        self.loggers = {}
        self.log_dir = self._get_log_dir()
        self._ensure_log_dir()
        self.file_handler = None
        self.console_handler = None
        self._setup_handlers()

    def _get_log_dir(self):
        """获取日志目录"""
        # 首先尝试程序运行目录
        exe_dir = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).parent.parent.parent
        log_dir = exe_dir / 'logs'
        return str(log_dir)

    def _ensure_log_dir(self):
        """确保日志目录存在"""
        if not os.path.exists(self.log_dir):
            try:
                os.makedirs(self.log_dir)
            except Exception as e:
                print(f"创建日志目录失败: {e}", file=sys.stderr)
                # 回退到临时目录
                import tempfile
                self.log_dir = tempfile.gettempdir()

    def _setup_handlers(self):
        """设置日志处理器"""
        # 文件处理器 - 按日期命名
        log_file = os.path.join(self.log_dir, f'three_kingdoms_{datetime.now().strftime("%Y%m%d")}.log')
        self.file_handler = logging.FileHandler(log_file, encoding='utf-8')
        self.file_handler.setLevel(LOG_LEVEL)
        self.file_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))

        # 控制台处理器
        self.console_handler = logging.StreamHandler(sys.stdout)
        self.console_handler.setLevel(LOG_LEVEL)
        self.console_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))

    def get_logger(self, name):
        """获取或创建日志记录器"""
        if name not in self.loggers:
            logger = logging.getLogger(name)
            logger.setLevel(LOG_LEVEL)
            logger.handlers = []  # 清除现有处理器
            logger.addHandler(self.file_handler)
            logger.addHandler(self.console_handler)
            logger.propagate = False  # 防止重复日志
            self.loggers[name] = logger
        return self.loggers[name]

    def get_log_file_path(self):
        """获取当前日志文件路径"""
        return os.path.join(self.log_dir, f'three_kingdoms_{datetime.now().strftime("%Y%m%d")}.log')


def get_logger(name):
    """获取日志记录器（全局函数）"""
    global _logger_manager
    if _logger_manager is None:
        _logger_manager = LoggerManager()
    return _logger_manager.get_logger(name)


def get_log_dir():
    """获取日志目录路径"""
    global _logger_manager
    if _logger_manager is None:
        _logger_manager = LoggerManager()
    return _logger_manager.log_dir
