import logging


class AppLogger:
    logger = logging.getLogger("kemea.rtspserver")
    def __init__(self):
        self.logger = logging.getLogger("kemea.rtspserver")
    def info(self, msg):
        self.logger.info(msg)
    def error(self, msg):
        self.logger.error(msg)

applogger = AppLogger()