from __future__ import annotations

from checkov.kubernetes.graph_builder.graph_components.edge_builders.K8SEdgeBuilder import K8SEdgeBuilder
from checkov.kubernetes.graph_builder.graph_components.blocks import KubernetesBlock
from checkov.kubernetes.kubernetes_utils import FILTERED_RESOURCES_FOR_EDGE_BUILDERS


class LabelSelectorEdgeBuilder(K8SEdgeBuilder):

    @staticmethod
    def should_search_for_edges(vertex: KubernetesBlock) -> bool:
        return vertex.metadata is not None \
            and vertex.metadata.labels is not None \
            and "kind" in vertex.attributes \
            and vertex.attributes["kind"] not in FILTERED_RESOURCES_FOR_EDGE_BUILDERS

    @staticmethod
    def find_connections(vertex: KubernetesBlock, vertices: list[KubernetesBlock]) -> list[int]:
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

        connections: list[int] = []

        if not vertex.metadata:
            return connections

        labels = vertex.metadata.labels
        for potential_vertex_index, potential_vertex in enumerate(vertices):
            if potential_vertex.id == vertex.id or not potential_vertex.metadata:
                continue

            match_labels = potential_vertex.metadata.selector.match_labels
            if match_labels:
                if len(match_labels) > len(labels):
                    continue
                # find shared label between the inspected vertex and the iterated potential vertex
                shared_labels = [k for k in match_labels if k in labels and match_labels[k] == labels[k]]
                if len(shared_labels) == len(match_labels):
                    # if all potential vertex's selector labels appear in vertex's labels - it's connected
                    connections.append(potential_vertex_index)

        return connections
