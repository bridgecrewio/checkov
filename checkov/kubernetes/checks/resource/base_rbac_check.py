from __future__ import annotations

from checkov.kubernetes.checks.resource.base_spec_check import BaseK8Check
from checkov.common.models.enums import CheckCategories, CheckResult
from typing import Dict, Any, List, TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable


class RbacOperation():
    """
    A collection of RBAC permissions that permit a certain operation within Kubernetes.
    For example, the RbacOperation below denotes a write operation on admission webhooks.
    control_webhooks = RbacOperation(
        apigroups=["admissionregistration.k8s.io"],
        verbs=["create", "update", "patch"],
        resources=["mutatingwebhookconfigurations", "validatingwebhookconfigurations"])
    Rules matching an apiGroup, verb and resource should be able to perform the operation.
    """
    __slots__ = ("apigroups", "resources", "verbs")

    def __init__(self, apigroups: List[str], verbs: List[str], resources: List[str]) -> None:
        self.apigroups = apigroups
        self.verbs = verbs
        self.resources = resources


class BaseRbacK8sCheck(BaseK8Check):
    """
    Base class for checks that evaluate RBAC permissions in Roles and ClusterRoles
    """
    def __init__(self, name: str, id: str, supported_entities: Iterable[str] | None = None) -> None:
        if supported_entities is None:
            supported_entities = ("Role", "ClusterRole")
        categories = (CheckCategories.KUBERNETES,)
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_entities)
        # A role that grants *ALL* the RbacOperation in failing_operations fails this check
        self.failing_operations: list[RbacOperation] = []

    def scan_spec_conf(self, conf: dict[str, Any]) -> CheckResult:
        rules = conf.get("rules")
        if rules and isinstance(rules, list):
            for operation in self.failing_operations:
                # if one operation can't be found, check passes
                if not any(self.rule_can(rule, operation) for rule in rules):
                    return CheckResult.PASSED
            # all operations were found, therefore the check fails
            return CheckResult.FAILED

        return CheckResult.PASSED

    # Check if a rule has an apigroup, verb, and resource specified in @operation
    def rule_can(self, rule: Dict[str, Any], operation: RbacOperation) -> bool:
        return self.apigroup_or_wildcard(rule, operation.apigroups) and \
            self.verb_or_wildcard(rule, operation.verbs) and \
            self.resource_or_wildcard(rule, operation.resources)

    def apigroup_or_wildcard(self, rule: Dict[str, Any], apigroups: List[str]) -> bool:
        return self.value_or_wildcard(rule, "apiGroups", apigroups)

    def verb_or_wildcard(self, rule: Dict[str, Any], verbs: List[str]) -> bool:
        return self.value_or_wildcard(rule, "verbs", verbs)

    def resource_or_wildcard(self, rule: Dict[str, Any], resources: List[str]) -> bool:
        if "resources" in rule:
            for granted_resource in rule["resources"]:
                if self.is_wildcard(granted_resource):
                    return True
                for failing_resource in resources:
                    if granted_resource == failing_resource:
                        return True
                    # Check for '*/subresource' syntax
                    if "/" in failing_resource and "/" in granted_resource:
                        if granted_resource == "*/" + failing_resource.split("/")[1]:
                            return True
        return False

    # Check if rule has a key with a wildcard or a value from @value_list
    def value_or_wildcard(self, rule: Dict[str, Any], key: str, value_list: List[str]) -> bool:
        if rule.get(key):
            for value in rule[key]:
                if self.is_wildcard(value) or value in value_list:
                    return True
        return False

    # Check if value is a K8s RBAC wildcard
    def is_wildcard(self, value: str) -> bool:
        return value == "*"
