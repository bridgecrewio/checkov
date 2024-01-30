import logging
import unittest

from checkov.common.logger_streams import LoggerStreams
from checkov.logging_init import log_stream, erase_log_stream

class TestLoggerStreams(unittest.TestCase):
    def test_stream_collect_valid_logs(self) -> None:
        log_message = 'this is a log message for testing'
        stream_name = 'main_stream'
        erase_log_stream()
        logger_streams = LoggerStreams()
        logger_streams.add_stream(stream_name, log_stream)
        logging.debug(log_message)

        # validate logs
        stream_content = logger_streams.get_streams().get(stream_name).getvalue()
        self.assertIn(log_message, stream_content)

        # validate eraser of logs
        erase_log_stream()
        stream_content = logger_streams.get_streams().get(stream_name).getvalue()
        self.assertEqual(stream_content, '')


if __name__ == "__main__":
    unittest.main()
