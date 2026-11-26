from __future__ import annotations

from dataclasses import dataclass
from typing import cast, Literal


@dataclass
class BlockType:
    RESOURCE: Literal["resource"] = "resource"
    MODULE: Literal["module"] = "module"
    DATA: Literal["data"] = "data"
    PROVIDER: Literal["provider"] = "provider"

    def get(self, attr_name: str) -> str:
        return cast("str", getattr(self, attr_name.upper()))
