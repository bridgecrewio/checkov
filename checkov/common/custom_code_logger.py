from __future__ import annotations

import os
from logging import Logger
from typing import Mapping, Any

from checkov.common.util.type_forcers import convert_str_to_bool


class CustomCodeLogger(Logger):
    """
    A custom logger designed to decide if we want to reduce some logs from the default logger.
    Could be used to reduce logs size.
    First use case is to log without the actual code of resources, which takes a lot of the logs size.
    The default is to log everything in order to keep api the same.
    """
    _SHOULD_LOG_CODE = convert_str_to_bool(os.environ.get("CHECKOV_ALLOW_CODE_LOGGING", True))
    CODE_TEMPLATES: list[str] = []
    CODE_MSG_REPLACEMENT = '<resource-code>'

    def info(
            self,
            msg: object,
            *args: object,
            exc_info: Any = None,
            stack_info: bool = False,
            stacklevel: int = 1,
            extra: Mapping[str, object] | None = None,
    ) -> None:
        if isinstance(msg, str) and not CustomCodeLogger._SHOULD_LOG_CODE:
            for code_template in CustomCodeLogger.CODE_TEMPLATES:
                msg.replace(code_template, CustomCodeLogger.CODE_MSG_REPLACEMENT)
        super().info(msg, *args, exc_info, stack_info, stacklevel, extra)
