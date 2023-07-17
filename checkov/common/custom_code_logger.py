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
    CODE_TEMPLATES: list[str] = []
    CODE_MSG_REPLACEMENT = '<resource-code>'

    def __init__(self, name: str, allow_code_logging: bool | None = None):
        super().__init__(name)
        if allow_code_logging is None:
            allow_code_logging = convert_str_to_bool(os.environ.get("CHECKOV_ALLOW_CODE_LOGGING", True))
        self._allow_code_logging = allow_code_logging

    def info(
            self,
            msg: object,
            *args: object,
            exc_info: Any = None,
            stack_info: bool = False,
            stacklevel: int = 1,
            extra: Mapping[str, object] | None = None,
    ) -> None:
        msg = self._remove_code_parts_from_msg(msg)
        super().info(msg, *args, exc_info, stack_info, stacklevel, extra)

    def debug(
            self,
            msg: object,
            *args: object,
            exc_info: Any = None,
            stack_info: bool = False,
            stacklevel: int = 1,
            extra: Mapping[str, object] | None = None,
        ) -> None:
        msg = self._remove_code_parts_from_msg(msg)
        super().debug(msg, *args, exc_info, stack_info, stacklevel, extra)

    def warning(
            self,
            msg: object,
            *args: object,
            exc_info: Any = None,
            stack_info: bool = False,
            stacklevel: int = 1,
            extra: Mapping[str, object] | None = None,
        ) -> None:
        msg = self._remove_code_parts_from_msg(msg)
        super().warning(msg, *args, exc_info, stack_info, stacklevel, extra)

    def warn(
            self,
            msg: object,
            *args: object,
            exc_info: Any = None,
            stack_info: bool = False,
            stacklevel: int = 1,
            extra: Mapping[str, object] | None = None,
        ) -> None:
        msg = self._remove_code_parts_from_msg(msg)
        super().warn(msg, *args, exc_info, stack_info, stacklevel, extra)

    def error(
            self,
            msg: object,
            *args: object,
            exc_info: Any = None,
            stack_info: bool = False,
            stacklevel: int = 1,
            extra: Mapping[str, object] | None = None,
        ) -> None:
        msg = self._remove_code_parts_from_msg(msg)
        super().error(msg, *args, exc_info, stack_info, stacklevel, extra)

    def exception(
            self,
            msg: object,
            *args: object,
            exc_info: Any = True,
            stack_info: bool = False,
            stacklevel: int = 1,
            extra: Mapping[str, object] | None = None,
        ) -> None:
        msg = self._remove_code_parts_from_msg(msg)
        super().exception(msg, *args, exc_info, stack_info, stacklevel, extra)

    def critical(
            self,
            msg: object,
            *args: object,            
            exc_info: Any = None,
            stack_info: bool = False,
            stacklevel: int = 1,
            extra: Mapping[str, object] | None = None,
        ) -> None:
        msg = self._remove_code_parts_from_msg(msg)
        super().critical(msg, *args, exc_info, stack_info, stacklevel, extra)

    def _remove_code_parts_from_msg(self, msg: object) -> object:
        if isinstance(msg, str) and not self._allow_code_logging:
            for code_template in CustomCodeLogger.CODE_TEMPLATES:
                msg = msg.replace(code_template, CustomCodeLogger.CODE_MSG_REPLACEMENT)
        return msg
