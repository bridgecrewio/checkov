from __future__ import annotations
from abc import abstractmethod

from checkov.kubernetes.graph_builder.graph_components.blocks import KubernetesBlock


class K8SEdgeBuilder:

    @abstractmethod
    def should_search_for_edges(self, vertex: KubernetesBlock) -> bool:
        """
        implementation should examine vertex's attributes and indicate if it's potentially
        suitable for the concrete class's edge type.
        e.g: search for a label attribute in LabelSelectorEdgeBuilder's implementation
        """
        raise NotImplementedError

    @abstractmethod
    def find_connection(self, vertex: KubernetesBlock, vertices: list[KubernetesBlock]) -> list[KubernetesBlock]:
        """
        implementation should search in each of the vertices for a possible connection
        to the vertex param according to the concrete class's rule(s).
        e.g: find vertices with a label attribute that match current vertex's selector attribute
        """
        raise NotImplementedError
