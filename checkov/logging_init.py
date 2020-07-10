import sys

import logging
import os


def init():
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'WARNING').upper()
    logging.basicConfig(level=LOG_LEVEL)
    logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
    rootLogger = logging.getLogger()
    consoleHandler = logging.StreamHandler(sys.stdout)
    consoleHandler.setFormatter(logFormatter)
    consoleHandler.setLevel(LOG_LEVEL)
    rootLogger.addHandler(consoleHandler)
    logging.getLogger("urllib3").setLevel(logging.ERROR)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)
    logging.getLogger("urllib3.connectionpool").propagate = False
    logging.getLogger("urllib3").propagate = False
