import logging
from unittest import mock

from checkov.common.resource_code_logger_filter import add_resource_code_filter_to_logger


TEST_CODE_TEMPLATES_TO_REPLACE = "THIS-SHOULD-BE-REPLACED!"


def test_code_logger_filter_do_not_log_if_not_allowed(caplog) -> None:
    with mock.patch("checkov.common.resource_code_logger_filter.ResourceCodeFilter.CODE_TEMPLATES",
                    [TEST_CODE_TEMPLATES_TO_REPLACE]):
        logger = logging.getLogger("code logging not allowed")
        add_resource_code_filter_to_logger(logger, allow_code_logging=False)
        logger.warning(TEST_CODE_TEMPLATES_TO_REPLACE)
        assert TEST_CODE_TEMPLATES_TO_REPLACE not in caplog.text


def test_code_logger_filter_logs_if_allowed(caplog) -> None:
    with mock.patch("checkov.common.resource_code_logger_filter.ResourceCodeFilter.CODE_TEMPLATES",
                    [TEST_CODE_TEMPLATES_TO_REPLACE]):
        logger = logging.getLogger("code logging allowed")
        add_resource_code_filter_to_logger(logger)
        logger.warning(TEST_CODE_TEMPLATES_TO_REPLACE)
        assert TEST_CODE_TEMPLATES_TO_REPLACE in caplog.text


def test_code_logger_filter_logs_based_on_arg_not_allowed(caplog) -> None:
    with mock.patch("checkov.common.resource_code_logger_filter.ResourceCodeFilter.CODE_TEMPLATES",
                    [TEST_CODE_TEMPLATES_TO_REPLACE]):
        logger = logging.getLogger("code logging not allowed")
        add_resource_code_filter_to_logger(logger, allow_code_logging=False)
        logger.warning(TEST_CODE_TEMPLATES_TO_REPLACE, extra={"mask": True})
        assert TEST_CODE_TEMPLATES_TO_REPLACE not in caplog.text
