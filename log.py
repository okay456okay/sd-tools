# Python Modules
import logging
import os

from config import LOG_LEVEL, LOG_FILE

class Logger(logging.Logger):
    FORMAT = "[%(asctime)-15s] %(name)s %(levelname)s (%(funcName)s(), %(filename)s:%(lineno)d): %(message)s"
    def __init__(self, name=None, level=None, log_file=None, *args, **kwargs):
        if name is None:
            super().__init__("Logger", *args, **kwargs)
        else:
            super().__init__(name, *args, **kwargs)

        self.init_logger(level, log_file)

    def init_logger(self, level=None, log_file=None):
        if level is None:
            level = logging.INFO
        self.setLevel(level)
        fomatter = logging.Formatter(self.FORMAT)
        if log_file is not None:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(level)
            file_handler.setFormatter(fomatter)
            self.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(fomatter)
        self.addHandler(console_handler)

logger = Logger(name="sd-tools", level=LOG_LEVEL, log_file=LOG_FILE)
