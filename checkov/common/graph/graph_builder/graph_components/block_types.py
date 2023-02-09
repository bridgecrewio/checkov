from __future__ import annotations

from dataclasses import dataclass
from typing import cast, TYPE_CHECKING

if TYPE_CHECKING:
    from typing_extensions import Literal


@dataclass
class BlockType:
    RESOURCE: Literal["resource"] = "resource"

    def get(self, attr_name: str) -> str:
        return cast("str", getattr(self, attr_name.upper()))
