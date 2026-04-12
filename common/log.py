# -*- coding: utf-8 -*-
# -----------------------------
# @Author    : 影子
# @Time      : 2025/3/10 10:55
# @Software  : PyCharm
# @FileName  : log.py
# -----------------------------
from loguru import logger
import os
from pathlib import Path


class Log:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.log_dir = self.base_dir / "logs"
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        logger.remove()
        logger.add(
            sink=str(self.log_dir / "{time:YYYY-MM-DD}.log"),
            rotation="1 day",
            retention="7 days",
            encoding="utf-8",
            level="INFO"
        )

        logger.add(
            sink=lambda msg: print(msg, end=""),
            level="INFO"
        )

    def info(self, message):
        logger.info(message)

    def debug(self, message):
        logger.debug(message)

    def warning(self, message):
        logger.warning(message)

    def error(self, message):
        logger.error(message)

    def critical(self, message):
        logger.critical(message)


log = Log()
