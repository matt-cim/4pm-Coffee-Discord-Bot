import logging
import sys
from typing import Optional

"""
Used to retrieve the logger. Must call initialize() first
"""

class Logger:
    logger = None

    @classmethod
    def initialize(cls):
        # init logging to stdout as well as a file
        file_handler = logging.FileHandler(filename="trace.log")
        stdout_handler = logging.StreamHandler(stream=sys.stdout)
        handlers = [file_handler, stdout_handler]
        logging.basicConfig(
            level=logging.INFO, 
            format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
            handlers=handlers
        )
        cls.logger = logging.getLogger()

    @classmethod
    def get_logger(cls) -> Optional[logging.Logger]:
        return cls.logger
    