from __future__ import annotations

from typing import TypeVar

FOREACH_STRING = 'for_each'
COUNT_STRING = 'count'
REFERENCES_VALUES = r"(var|module|local)\."
FOR_EACH_BLOCK_TYPE = TypeVar("FOR_EACH_BLOCK_TYPE", bound="dict[int, Optional[list[str] | dict[str, Any] | int]]")
COUNT_KEY = 'count.index'
EACH_KEY = 'each.key'
EACH_VALUE = 'each.value'
