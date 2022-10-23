from __future__ import annotations

from checkov.kubernetes.graph_builder.graph_components.K8SEdgeBuilder import K8SEdgeBuilder
from checkov.kubernetes.graph_builder.graph_components.blocks import KubernetesBlock


class LabelSelectorEdgeBuilder(K8SEdgeBuilder):

    @staticmethod
    def should_search_for_edges(vertex: KubernetesBlock) -> bool:
        if vertex.metadata.labels is not None:
            return True
        return False

    @staticmethod
    def find_connections(vertex: KubernetesBlock, vertices: list[KubernetesBlock]) -> list[KubernetesBlock]:
        """
        connection is defined when all vertex's match_labels are matched to another vertex's labels.

        example #1:
            object A match_labels - {label1: "foo", label2: "bar"}
            object B labels       - {label1: "foo", label2: "bar", label3: "baz"}
        A and B are connected because all A's match_labels appear in B's labels

        example #2:
            object C match_labels - {label1: "foo", label2: "bar", label3: "baz"}
            object D labels       - {label1: "foo", label2: "bar"}
        C and D are not connected since Not all C's match_labels appear in D's labels
        """

        connections: list[KubernetesBlock] = []
        labels = vertex.metadata.labels
        for potential_vertex in vertices:
            match_labels = potential_vertex.metadata.selector.match_labels
            if match_labels and potential_vertex.id != vertex.id:
                shared_labels = {k: match_labels[k] for k in match_labels if k in labels and match_labels[k] == labels[k]}
                if len(shared_labels) == len(match_labels):
                    connections.append(potential_vertex)

        return connections
