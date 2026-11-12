from __future__ import annotations

import re
from typing import Any

from checkov.kubernetes.graph_builder.graph_components.edge_builders.K8SEdgeBuilder import K8SEdgeBuilder
from checkov.kubernetes.graph_builder.graph_components.blocks import KubernetesBlock

CILIUM_NETWORK_POLICY_KINDS = ("CiliumNetworkPolicy", "CiliumClusterwideNetworkPolicy")

# Cilium exposes a pod's Kubernetes namespace under this virtual label
K8S_NAMESPACE_LABEL = "io.kubernetes.pod.namespace"
# Cilium exposes a pod's service account under this virtual label; it is derived
# from the pod spec's serviceAccountName, not from metadata.labels
K8S_SERVICE_ACCOUNT_LABEL = "io.cilium.k8s.policy.serviceaccount"
# Cilium's default label source prefix for Kubernetes pod labels
K8S_LABEL_PREFIX = "k8s:"

# Cilium derives further virtual labels that cannot be resolved from a pod
# manifest; selectors using them are unresolvable here and must fail closed
# (https://docs.cilium.io/en/v1.16/security/policy/kubernetes/)
UNRESOLVABLE_VIRTUAL_LABELS = frozenset({
    "io.cilium.k8s.policy.cluster",  # the cluster name is runtime context
})
UNRESOLVABLE_VIRTUAL_LABEL_PREFIXES = (
    "io.cilium.k8s.namespace.labels.",  # labels of the Namespace object, not the pod
)

# Kubernetes label key (name part) and value syntax
# (https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/)
LABEL_NAME_PATTERN = re.compile(r"^([A-Za-z0-9]([-A-Za-z0-9_.]*[A-Za-z0-9])?)?$")

# sentinel for selector keys or values that cannot be resolved from a manifest
# (unknown label source prefixes, unresolvable pod context); distinct from a
# valid label that is simply absent
UNSUPPORTED = object()


class CiliumNetworkPolicyEdgeBuilder(K8SEdgeBuilder):
    """Connects Cilium network policies to the Pods they select.

    Cilium semantics differ from Kubernetes NetworkPolicy:
    - the selecting field is `endpointSelector`, not `podSelector`
    - the selector lives under `spec.endpointSelector` or under each entry of a
      `specs` list (both forms exist for CiliumNetworkPolicy and
      CiliumClusterwideNetworkPolicy)
    - a CiliumNetworkPolicy only selects endpoints in its own namespace, while a
      CiliumClusterwideNetworkPolicy selects endpoints cluster-wide; a
      cluster-wide policy can target a namespace via the virtual label
      `k8s:io.kubernetes.pod.namespace`
    - an empty endpointSelector ({}) selects all endpoints in scope
    - matchLabels and matchExpressions are ANDed with Kubernetes label selector
      semantics; a malformed or unresolvable requirement makes the whole
      selector match nothing, so an invalid policy can never silence the check
    - a policy without any endpointSelector (for example a host policy selecting
      nodes via nodeSelector) selects no Pods within the scope of this check
      and produces no connections
    """

    @staticmethod
    def should_search_for_edges(vertex: KubernetesBlock) -> bool:
        return bool(vertex.attributes.get("kind") in CILIUM_NETWORK_POLICY_KINDS)

    @staticmethod
    def find_connections(vertex: KubernetesBlock, vertices: list[KubernetesBlock]) -> list[int]:
        connections: list[int] = []

        attributes = vertex.attributes
        is_clusterwide = attributes.get("kind") == "CiliumClusterwideNetworkPolicy"
        metadata = attributes.get("metadata") or {}
        policy_namespace = metadata.get("namespace") or "default"

        # collect every endpointSelector the policy defines (spec and specs list forms)
        selectors: list[Any] = []
        spec = attributes.get("spec")
        if isinstance(spec, dict) and "endpointSelector" in spec:
            selectors.append(spec.get("endpointSelector"))
        specs = attributes.get("specs")
        if isinstance(specs, list):
            for entry in specs:
                if isinstance(entry, dict) and "endpointSelector" in entry:
                    selectors.append(entry.get("endpointSelector"))
        if not selectors:
            # no endpointSelector anywhere (e.g. a nodeSelector host policy):
            # selects no Pods within this check's scope, so it must not silence it
            return connections

        for potential_pod_index, potential_vertex in enumerate(vertices):
            if potential_vertex.id == vertex.id or potential_vertex.attributes.get("kind") != "Pod":
                continue

            pod = potential_vertex
            pod_metadata = pod.attributes.get("metadata") or {}
            pod_namespace = pod_metadata.get("namespace") or "default"
            if not is_clusterwide and pod_namespace != policy_namespace:
                continue

            pod_labels = CiliumNetworkPolicyEdgeBuilder._effective_pod_labels(pod.attributes, pod_metadata, pod_namespace)
            for selector in selectors:
                if CiliumNetworkPolicyEdgeBuilder._selector_matches(selector, pod_labels):
                    connections.append(potential_pod_index)
                    break

        return connections

    @staticmethod
    def _effective_pod_labels(pod_attributes: dict[str, Any], pod_metadata: dict[str, Any], pod_namespace: str) -> dict[str, Any]:
        """Pod labels as Cilium sees them: string Kubernetes labels plus the
        virtual namespace and service account labels, without internal
        bookkeeping keys."""

        raw_labels = pod_metadata.get("labels")
        labels: dict[str, Any] = {
            k: v
            for k, v in raw_labels.items()
            if isinstance(k, str) and not k.startswith("__") and isinstance(v, str)
        } if isinstance(raw_labels, dict) else {}
        labels[K8S_NAMESPACE_LABEL] = pod_namespace
        pod_spec = pod_attributes.get("spec")
        if isinstance(pod_spec, dict):
            service_account = pod_spec.get("serviceAccountName")
            labels[K8S_SERVICE_ACCOUNT_LABEL] = service_account if isinstance(service_account, str) and service_account else "default"
        else:
            # the pod spec cannot be read, so the service account cannot be resolved
            labels[K8S_SERVICE_ACCOUNT_LABEL] = UNSUPPORTED
        return labels

    @staticmethod
    def _selector_matches(selector: Any, pod_labels: dict[str, Any]) -> bool:
        if not isinstance(selector, dict):
            return False

        match_labels = selector.get("matchLabels")
        match_expressions = selector.get("matchExpressions")
        # validate forms before evaluating: malformed collections are invalid,
        # only a genuinely empty selector ({}) selects all endpoints in scope
        if match_labels is not None and not isinstance(match_labels, dict):
            return False
        if match_expressions is not None and not isinstance(match_expressions, list):
            return False
        if not match_labels and not match_expressions:
            return True

        # every requirement has to match; an invalid requirement matches nothing
        if match_labels and not all(
            CiliumNetworkPolicyEdgeBuilder._match_label(key, value, pod_labels)
            for key, value in match_labels.items()
            if not (isinstance(key, str) and key.startswith("__"))  # internal bookkeeping keys
        ):
            return False
        if match_expressions and not all(
            CiliumNetworkPolicyEdgeBuilder._match_expression(expression, pod_labels)
            for expression in match_expressions
        ):
            return False
        return True

    @staticmethod
    def _is_valid_label_value(value: Any) -> bool:
        return isinstance(value, str) and len(value) <= 63 and LABEL_NAME_PATTERN.match(value) is not None

    @staticmethod
    def _match_label(key: Any, value: Any, pod_labels: dict[str, Any]) -> bool:
        if not CiliumNetworkPolicyEdgeBuilder._is_valid_label_value(value):
            return False
        label_value = CiliumNetworkPolicyEdgeBuilder._label_value(key, pod_labels)
        return label_value is not UNSUPPORTED and label_value == value

    @staticmethod
    def _normalize_key(key: Any) -> Any:
        """Normalizes a selector key: strips Cilium's `k8s:` source prefix and
        validates the remaining key form (Kubernetes label key syntax). Returns
        the UNSUPPORTED sentinel for keys with other source prefixes (reserved:,
        any:, ...) or malformed keys; callers must treat UNSUPPORTED as an
        invalid requirement that matches nothing, never as a missing label."""

        if not isinstance(key, str) or key.startswith("__"):
            return UNSUPPORTED
        if key.startswith(K8S_LABEL_PREFIX):
            key = key[len(K8S_LABEL_PREFIX):]
        elif ":" in key.split("/", 1)[0]:
            return UNSUPPORTED
        if not key or len(key) > 253:
            return UNSUPPORTED
        name = key.rsplit("/", 1)[-1]
        if not 0 < len(name) <= 63 or LABEL_NAME_PATTERN.match(name) is None:
            return UNSUPPORTED
        return key

    @staticmethod
    def _label_value(key: Any, pod_labels: dict[str, Any]) -> Any:
        """Resolves a selector key against pod labels. Known Cilium virtual
        label families that cannot be resolved from a pod manifest (cluster
        name, namespace labels) return UNSUPPORTED and fail closed; they are
        not treated as ordinary missing labels."""

        normalized = CiliumNetworkPolicyEdgeBuilder._normalize_key(key)
        if normalized is UNSUPPORTED:
            return UNSUPPORTED
        if normalized in UNRESOLVABLE_VIRTUAL_LABELS or normalized.startswith(UNRESOLVABLE_VIRTUAL_LABEL_PREFIXES):
            return UNSUPPORTED
        return pod_labels.get(normalized)

    @staticmethod
    def _match_expression(expression: Any, pod_labels: dict[str, Any]) -> bool:
        """Evaluates a single matchExpressions requirement against the pod labels.
        An invalid or unresolvable requirement makes the whole selector invalid,
        therefore it doesn't match any pod. Operator semantics follow the
        Kubernetes label selector: a valid NotIn or DoesNotExist requirement
        still matches when the pod simply lacks the (ordinary) label."""

        if not isinstance(expression, dict):
            return False

        key = expression.get("key")
        operator = expression.get("operator")
        values = expression.get("values")
        label_value = CiliumNetworkPolicyEdgeBuilder._label_value(key, pod_labels)
        if label_value is UNSUPPORTED:
            # the key can never be resolved from a manifest (a label source
            # other than k8s:, or an unresolvable virtual label); the
            # requirement is invalid and matches nothing, whatever the operator
            return False
        if operator in ("In", "NotIn"):
            if not values or not isinstance(values, list) or not all(
                CiliumNetworkPolicyEdgeBuilder._is_valid_label_value(v) for v in values
            ):
                return False
            if operator == "In":
                return label_value is not None and label_value in values
            return label_value is None or label_value not in values
        if operator in ("Exists", "DoesNotExist"):
            if values is not None and values != []:
                return False
            if operator == "Exists":
                return label_value is not None
            return label_value is None

        return False
