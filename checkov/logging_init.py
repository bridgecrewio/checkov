import logging
import os
from io import StringIO

from checkov.common.resource_code_logger_filter import add_resource_code_filter_to_logger

LOG_LEVEL = os.getenv('LOG_LEVEL', 'WARNING').upper()
logging.basicConfig(level=LOG_LEVEL)
log_formatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
root_logger = logging.getLogger()
add_resource_code_filter_to_logger(root_logger)
stream_handler = root_logger.handlers[0]
stream_handler.setFormatter(log_formatter)
stream_handler.setLevel(LOG_LEVEL)
root_logger.setLevel(logging.DEBUG)
logging.getLogger().setLevel(logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.ERROR)
logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)
logging.getLogger("urllib3.connectionpool").propagate = False
logging.getLogger("urllib3").propagate = False
log_stream = StringIO()
stream_handler = logging.StreamHandler(stream=log_stream)
stream_handler.setFormatter(log_formatter)
stream_handler.setLevel(logging.DEBUG)
root_logger.addHandler(stream_handler)


def erase_log_stream() -> None:
    log_stream.seek(0)
    log_stream.truncate(0)
