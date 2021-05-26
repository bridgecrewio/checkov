import sys

import logging
import os


def init():
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'WARNING').upper()
    logging.basicConfig(level=LOG_LEVEL)
    log_formatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
    root_logger = logging.getLogger()
    stream_handler = root_logger.handlers[0]
    stream_handler.setFormatter(log_formatter)
    root_logger.setLevel(LOG_LEVEL)
    logging.getLogger().setLevel(LOG_LEVEL)
    logging.getLogger("urllib3").setLevel(logging.ERROR)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)
    logging.getLogger("urllib3.connectionpool").propagate = False
    logging.getLogger("urllib3").propagate = False
