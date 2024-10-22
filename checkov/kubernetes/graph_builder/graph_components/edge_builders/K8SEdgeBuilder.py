from __future__ import annotations
from abc import abstractmethod

from checkov.kubernetes.graph_builder.graph_components.blocks import KubernetesBlock


class K8SEdgeBuilder:

    @staticmethod
    @abstractmethod
    def should_search_for_edges(vertex: KubernetesBlock) -> bool:
        """
        implementation should examine vertex's attributes and indicate if it's potentially
        suitable for the concrete class's edge type.
        e.g: search for a label attribute in LabelSelectorEdgeBuilder's implementation
        """
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def find_connections(vertex: KubernetesBlock, vertices: list[KubernetesBlock]) -> list[int]:
        """
        implementation should search in each of the vertices for a possible connection
        to the vertex param according to the concrete class's rule(s).
        returns a list of the connected vertices' indices
        e.g: find vertices with a label attribute that match current vertex's selector attribute
        """
        raise NotImplementedError
