from __future__ import annotations

from typing import Optional, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from typing_extensions import TypeAlias

FOREACH_STRING = 'for_each'
COUNT_STRING = 'count'
REFERENCES_VALUES = r"(var|module|local)\."
FOR_EACH_BLOCK_TYPE: TypeAlias = "dict[int, Optional[list[str] | dict[str, Any] | int]]"
COUNT_KEY = 'count.index'
EACH_KEY = 'each.key'
EACH_VALUE = 'each.value'
VIRTUAL_RESOURCE = 'virtual_resource'
