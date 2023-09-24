from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from checkov.common.models.enums import GraphCheckExtension


class BaseGraphCheckExtension(ABC):
    name: GraphCheckExtension  # noqa: CCE003  # a static attribute

    @abstractmethod
    def extend(self, vertex_data: dict[str, Any]) -> dict[str, Any]:
        pass
