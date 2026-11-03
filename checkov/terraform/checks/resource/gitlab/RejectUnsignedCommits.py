from typing import Any

from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


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


class RejectUnsignedCommits(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure GitLab commits are signed"
        id = "CKV_GLB_4"
        supported_resources = ["gitlab_project"]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.FAILED)

    def get_inspected_key(self) -> str:
        return "push_rules/[0]/reject_unsigned_commits"

    def get_expected_value(self) -> Any:
        return True

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        if self._has_enabled_push_rules(conf):
            return CheckResult.PASSED
        return super().scan_resource_conf(conf)

    def _has_enabled_push_rules(self, conf: dict[str, list[Any]]) -> bool:
        # gitlabhq/gitlab 19 deprecates the push_rules block on
        # gitlab_project; the control lives on gitlab_project_push_rules
        # resources that reference the project. Accept those alongside
        # the legacy block so projects on older providers keep passing.
        address = _project_address(conf)
        if not address or self.graph is None:
            return False
        for _, node in self.graph.nodes():
            if node.get(CustomAttributes.RESOURCE_TYPE) != "gitlab_project_push_rules":
                continue
            if _reference_address(node.get("project")) != address:
                continue
            enabled = node.get("reject_unsigned_commits")
            if isinstance(enabled, list):
                enabled = enabled[0] if enabled else None
            if enabled is True:
                return True
        return False


check = RejectUnsignedCommits()
