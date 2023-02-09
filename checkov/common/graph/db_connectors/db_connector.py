from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, TypeVar, Generic

if TYPE_CHECKING:
    from checkov.common.graph.graph_builder.graph_components.blocks import Block  # noqa
    from checkov.common.graph.graph_builder.local_graph import LocalGraph

T = TypeVar("T")
_Block = TypeVar("_Block", bound="Block")


class DBConnector(ABC, Generic[T]):
    @abstractmethod
    def save_graph(self, local_graph: LocalGraph[_Block]) -> T:
        pass

    @abstractmethod
    def get_reader_endpoint(self) -> T:
        pass

    @abstractmethod
    def get_writer_endpoint(self) -> T:
        pass

    @abstractmethod
    def disconnect(self) -> None:
        pass
