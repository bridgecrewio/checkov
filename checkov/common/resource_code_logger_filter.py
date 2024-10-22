from __future__ import annotations

import os
from logging import Logger, Filter, LogRecord

from checkov.common.util.type_forcers import convert_str_to_bool


class ResourceCodeFilter(Filter):
    """
    A custom logger filter designed to decide if we want to filter some logs from the default logger.
    Could be used to reduce logs size.
    First use case is to log without the actual code of resources, which takes a lot of the logs size.
    The default is to log everything in order to keep api the same.
    """
    CODE_TEMPLATES: list[str] = []

    def __init__(self, allow_code_logging: bool = True):
        super().__init__()
        self.allow_code_logging = allow_code_logging

    def filter(self, record: LogRecord) -> bool:
        if self.allow_code_logging:
            return True
        if hasattr(record, "mask"):
            # Allows filtering using `logging.info("<msg>", extra={"mask": True})`
            mask = record.mask
            if not isinstance(mask, bool):
                raise Exception(f"Expected to get `mask` as boolean for logging function, instead got: {mask} of type {type(mask)}")
            return not record.mask

        msg = record.msg
        return self._filter_based_on_msg(msg)

    def _filter_based_on_msg(self, msg: str) -> bool:
        for code_template in ResourceCodeFilter.CODE_TEMPLATES:
            if code_template in msg:
                return False
        return True


def add_resource_code_filter_to_logger(logger: Logger, allow_code_logging: bool | None = None) -> None:
    if allow_code_logging is None:
        allow_code_logging_res = convert_str_to_bool(os.environ.get("CHECKOV_ALLOW_CODE_LOGGING", True))
        if isinstance(allow_code_logging_res, bool):
            allow_code_logging = allow_code_logging_res
        else:
            raise Exception(f"Failed to get correct result for env variable - `CHECKOV_ALLOW_CODE_LOGGING`. "
                            f"Got {allow_code_logging_res}")

    resource_code_filter = ResourceCodeFilter(allow_code_logging=allow_code_logging)
    logger.addFilter(resource_code_filter)
