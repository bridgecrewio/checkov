import logging
import os
from io import StringIO

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
log_stream = StringIO()
stream_handler = logging.StreamHandler(stream=log_stream)
stream_handler.setFormatter(log_formatter)
stream_handler.setLevel(logging.DEBUG)
root_logger.addHandler(stream_handler)
