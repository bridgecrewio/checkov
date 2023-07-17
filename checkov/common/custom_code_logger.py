from __future__ import annotations

import os
from logging import Logger, LoggerAdapter
from typing import Any, MutableMapping

from checkov.common.util.type_forcers import convert_str_to_bool


class RemoveCodeInstancesLoggerAdapter(LoggerAdapter):
    """
        A custom logger adapter designed to decide if we want to reduce some logs from the default logger.
        Could be used to reduce logs size.
        First use case is to log without the actual code of resources, which takes a lot of the logs size.
        The default is to log everything in order to keep api the same.
        """
    CODE_TEMPLATES: list[str] = []
    CODE_MSG_REPLACEMENT = '<resource-code>'

    def __init__(self, logger: Logger, allow_code_logging: bool | None = None):
        super().__init__(logger)
        if allow_code_logging is None:
            allow_code_logging = convert_str_to_bool(os.environ.get("CHECKOV_ALLOW_CODE_LOGGING", True))
        self._allow_code_logging = allow_code_logging

    def process(self, msg: Any, kwargs: MutableMapping[str, Any]) -> tuple[Any, MutableMapping[str, Any]]:
        if isinstance(msg, str) and not self._allow_code_logging:
            for code_template in RemoveCodeInstancesLoggerAdapter.CODE_TEMPLATES:
                msg = msg.replace(code_template, RemoveCodeInstancesLoggerAdapter.CODE_MSG_REPLACEMENT)
        return msg, kwargs


def get_logger_with_code_adapter(logger: Logger, allow_code_logging: bool) -> RemoveCodeInstancesLoggerAdapter:
    return RemoveCodeInstancesLoggerAdapter(logger, allow_code_logging=allow_code_logging)
