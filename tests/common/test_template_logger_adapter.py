import logging

import mock
import pytest

from checkov.common.template_logger_adapter import get_logger_with_template_adapter, TemplatesLoggerAdapter


TEST_CODE_TEMPLATES_TO_REPLACE = "THIS-SHOULD-BE-REPLACED!"


@pytest.fixture()
def logger() -> logging.Logger:
    logger = logging.getLogger("testing")
    return logger


def test_logger_adapter_removes_custom_parts_from_msg(caplog, logger: logging.Logger) -> None:
    with mock.patch("checkov.common.template_logger_adapter.TemplatesLoggerAdapter.CODE_TEMPLATES",
                    [TEST_CODE_TEMPLATES_TO_REPLACE]):
        code_logger_adapter = get_logger_with_template_adapter(logger, allow_code_logging=False)
        code_logger_adapter.warning(TEST_CODE_TEMPLATES_TO_REPLACE)
        assert TEST_CODE_TEMPLATES_TO_REPLACE not in caplog.text
        assert TemplatesLoggerAdapter.CODE_MSG_REPLACEMENT in caplog.text


def test_logger_adapter_does_not_remove_msg_if_allow_code_logging_enabled(caplog, logger: logging.Logger) -> None:
    with mock.patch("checkov.common.template_logger_adapter.TemplatesLoggerAdapter.CODE_TEMPLATES",
                    [TEST_CODE_TEMPLATES_TO_REPLACE]):
        code_logger_adapter = get_logger_with_template_adapter(logger)
        code_logger_adapter.warning(TEST_CODE_TEMPLATES_TO_REPLACE)
        assert TEST_CODE_TEMPLATES_TO_REPLACE in caplog.text
        assert TemplatesLoggerAdapter.CODE_MSG_REPLACEMENT not in caplog.text


