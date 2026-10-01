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
    def _pod_matches_selector(pod: KubernetesBlock, pod_selector: dict[str, Any]) -> bool:
        """
        Implements the standard Kubernetes LabelSelector semantics for a NetworkPolicy podSelector.
        A pod is selected only when every matchLabels entry and every matchExpressions requirement
        is satisfied. An empty selector selects all pods.
        """

        match_labels = pod_selector.get("matchLabels")
        if not isinstance(match_labels, dict):
            match_labels = {}
        remove_metadata_from_attribute(match_labels)

        match_expressions = pod_selector.get("matchExpressions")
        if not isinstance(match_expressions, list):
            match_expressions = []

        pod_labels = pod.metadata.labels if pod.metadata is not None else None
        if not isinstance(pod_labels, dict):
            pod_labels = {}

        for key, value in match_labels.items():
            if pod_labels.get(key) != value:
                return False

        for requirement in match_expressions:
            if not isinstance(requirement, dict):
                # malformed requirement, we can't prove the pod is selected
                return False
            key = requirement.get("key")
            operator = requirement.get("operator")
            values = requirement.get("values")
            if not isinstance(values, list):
                values = []
            has_key = key in pod_labels
            if operator == "In":
                if not has_key or pod_labels[key] not in values:
                    return False
            elif operator == "NotIn":
                if has_key and pod_labels[key] in values:
                    return False
            elif operator == "Exists":
                if not has_key:
                    return False
            elif operator == "DoesNotExist":
                if has_key:
                    return False
            else:
                # unknown operator - the pod can't be proven to be selected
                return False
        return True

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

        the podSelector is evaluated with the standard Kubernetes LabelSelector semantics,
        which includes both matchLabels and matchExpressions. every requirement has to be
        satisfied for the pod to be selected by the policy.
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

            if NetworkPolicyEdgeBuilder._pod_matches_selector(pod, pod_selector):
                connections.append(potential_pod_index)

        return connections
