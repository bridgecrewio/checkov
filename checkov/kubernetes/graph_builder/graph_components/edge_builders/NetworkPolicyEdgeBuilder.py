from __future__ import annotations

from checkov.kubernetes.graph_builder.graph_components.edge_builders.K8SEdgeBuilder import K8SEdgeBuilder
from checkov.kubernetes.graph_builder.graph_components.blocks import KubernetesBlock
from checkov.kubernetes.kubernetes_utils import remove_metadata_from_attribute


class NetworkPolicyEdgeBuilder(K8SEdgeBuilder):

    @staticmethod
    def should_search_for_edges(vertex: KubernetesBlock) -> bool:
        return bool(vertex.attributes.get("kind") == "NetworkPolicy")

    @staticmethod
    def find_connections(vertex: KubernetesBlock, vertices: list[KubernetesBlock]) -> list[int]:
        """
        this edge builder is a specific case of LabelSelectorEdgeBuilder with 2 differences:
        1. it applies only to NetworkPolicy resources that connect to Pod resources
        2. it handles a wildcard that attaches a NetworkPolicy resource to all pods. for example:

        apiVersion: networking.k8s.io/v1
        kind: NetworkPolicy
        metadata:
          name: default-deny-ingress
        spec:
          podSelector: {}
          policyTypes:
          - Ingress
        """

        connections: list[int] = []
        for potential_pod_index, potential_vertex in enumerate(vertices):
            if potential_vertex.id == vertex.id or potential_vertex.attributes.get("kind") != "Pod":
                continue

            network_policy = vertex
            pod = potential_vertex

            pod_spec = network_policy.attributes.get("spec", {})
            if pod_spec is None:
                continue
            pod_selector = pod_spec.get("podSelector")
            if not pod_selector:
                continue
            match_labels = pod_selector.get("matchLabels")
            remove_metadata_from_attribute(match_labels)

            # the network policy has specific pod labels
            if match_labels and pod.metadata is not None and pod.metadata.labels is not None:
                pod_labels = pod.metadata.labels
                if len(match_labels) > len(pod_labels):
                    continue
                # find shared label between the inspected vertex and the iterated potential vertex
                shared_labels = [k for k in match_labels if k in pod_labels and match_labels[k] == pod_labels[k]]
                if len(shared_labels) == len(match_labels):
                    connections.append(potential_pod_index)
            # the network policy has a podSelector property with no labels and should apply for all pods
            else:
                connections.append(potential_pod_index)

        return connections
