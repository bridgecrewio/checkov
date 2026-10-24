from __future__ import annotations

from typing import Any

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
            match_expressions = pod_selector.get("matchExpressions")

            # the network policy has a podSelector property with no labels and should apply for all pods
            if not match_labels and not match_expressions:
                connections.append(potential_pod_index)
                continue

            # the network policy has specific pod labels and/or expressions, all of them have to match
            # an invalid selector doesn't match any pod
            if match_labels and not isinstance(match_labels, dict):
                continue
            if match_expressions and not isinstance(match_expressions, list):
                continue
            pod_labels = pod.metadata.labels if pod.metadata is not None and pod.metadata.labels is not None else {}
            if match_labels and not all(k in pod_labels and pod_labels[k] == v for k, v in match_labels.items()):
                continue
            if match_expressions and not all(
                NetworkPolicyEdgeBuilder._match_expression(expression, pod_labels) for expression in match_expressions
            ):
                continue
            connections.append(potential_pod_index)

        return connections

    @staticmethod
    def _match_expression(expression: Any, pod_labels: dict[str, Any]) -> bool:
        """
        evaluates a single matchExpressions requirement against the pod labels.
        an invalid requirement makes the whole selector invalid, therefore it doesn't match any pod.
        """

        if not isinstance(expression, dict):
            return False

        key = expression.get("key")
        operator = expression.get("operator")
        values = expression.get("values")
        if not isinstance(key, str):
            return False
        if operator in ("In", "NotIn"):
            if not values or not isinstance(values, list):
                return False
            if operator == "In":
                return key in pod_labels and pod_labels[key] in values
            return key not in pod_labels or pod_labels[key] not in values
        if operator in ("Exists", "DoesNotExist"):
            if values:
                return False
            if operator == "Exists":
                return key in pod_labels
            return key not in pod_labels

        return False
