from __future__ import annotations

from typing import Any

from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceCheck
from checkov.common.util.type_forcers import force_int


def _project_address(conf: dict[str, list[Any]]) -> str | None:
    address = conf.get("__address__")
    if isinstance(address, list):
        address = address[0] if address else None
    return address if isinstance(address, str) else None


def _reference_address(value: Any) -> str | None:
    """Normalize a Terraform reference to the address it points at.

    Graph node attributes hold references as plain strings such as
    "gitlab_project.this.id". Returns the address without the trailing
    attribute, or None when the value is not a plain reference.
    """
    if isinstance(value, list):
        value = value[0] if value else None
    if not isinstance(value, str):
        return None
    value = value.strip()
    if value.startswith("${") and value.endswith("}"):
        value = value[2:-1].strip()
    if value.endswith(".id"):
        value = value[:-3]
    return value or None


class RequireTwoApprovalsToMerge(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure at least two approving reviews are required to merge a GitLab MR"
        id = "CKV_GLB_1"
        supported_resources = ["gitlab_project"]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        approvals = conf.get("approvals_before_merge")
        if approvals and isinstance(approvals, list):
            num_approvals = force_int(approvals[0])
            if num_approvals and num_approvals >= 2:
                return CheckResult.PASSED
        if self._has_qualifying_approval_rule(conf):
            return CheckResult.PASSED
        self.evaluated_keys = ["approvals_before_merge"]
        return CheckResult.FAILED

    def _has_qualifying_approval_rule(self, conf: dict[str, list[Any]]) -> bool:
        # Since gitlabhq/gitlab 19 the approvals_before_merge argument is
        # gone from gitlab_project; the control lives on
        # gitlab_project_approval_rule resources that reference the
        # project. Accept those alongside the legacy argument so
        # projects on older providers keep passing.
        address = _project_address(conf)
        if not address or self.graph is None:
            return False
        for _, node in self.graph.nodes():
            if node.get(CustomAttributes.RESOURCE_TYPE) != "gitlab_project_approval_rule":
                continue
            if _reference_address(node.get("project")) != address:
                continue
            required = node.get("approvals_required")
            if isinstance(required, list):
                required = required[0] if required else None
            if required is None:
                continue
            num_required = force_int(required)
            if num_required and num_required >= 2:
                return True
        return False


check = RequireTwoApprovalsToMerge()
