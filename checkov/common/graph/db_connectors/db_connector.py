from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar, Generic

if TYPE_CHECKING:
    from checkov.common.graph.graph_builder.local_graph import LocalGraph

T = TypeVar("T")


class DBConnector(Generic[T]):
    def save_graph(self, local_graph: LocalGraph) -> T:
        pass

    def get_reader_endpoint(self) -> T:
        pass

    def get_writer_endpoint(self) -> T:
        pass

    def disconnect(self) -> None:
        pass
