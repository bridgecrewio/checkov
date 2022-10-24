from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, TypeVar, Generic, TYPE_CHECKING

if TYPE_CHECKING:
    from checkov.common.graph.graph_builder.graph_components.block_types import BlockType  # noqa

_BlockT = TypeVar("_BlockT", bound="BlockType")


class VertexReference(ABC, Generic[_BlockT]):
    __slots__ = ("block_type", "sub_parts", "origin_value")

    def __init__(self, block_type: str | _BlockT, sub_parts: list[str], origin_value: str) -> None:
        self.block_type: _BlockT = self.block_type_str_to_enum(block_type) if isinstance(block_type, str) else block_type
        self.sub_parts = sub_parts
        self.origin_value = origin_value

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, VertexReference):
            return False
        return (
            self.block_type == other.block_type
            and self.sub_parts == other.sub_parts
            and self.origin_value == other.origin_value
        )

    def __str__(self) -> str:
        return f"{self.block_type} sub_parts = {self.sub_parts}, origin = {self.origin_value}"

    @staticmethod
    @abstractmethod
    def block_type_str_to_enum(block_type_str: str) -> _BlockT:
        pass
