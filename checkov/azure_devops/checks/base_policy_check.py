from __future__ import annotations

from typing import Any
from abc import abstractmethod

from bc_jsonpath_ng import parse

from checkov.azure_devops.checks.base_azure_devops_check import BaseAzureDevOpsCheck
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.json_doc.enums import BlockType

MESSAGE_BRANCH_NOT_PROTECTED = "Branch not protected"


class BasePolicyCheck(BaseAzureDevOpsCheck):
    def __init__(self, id: str, name: str, policy_type_id: str) -> None:
        super().__init__(
            id=id,
            name=name,
            categories=(CheckCategories.SUPPLY_CHAIN,),
            supported_entities=("*",),
            block_type=BlockType.DOCUMENT,
        )
        self.policy_type_id = policy_type_id

    def scan_entity_conf(self, conf: list[dict[str, Any]], entity_type: str) -> CheckResult:  # type:ignore[override]
        if not isinstance(conf, list):
            return CheckResult.UNKNOWN  # maybe better to return FAILED

        evaluated_key = self.get_evaluated_keys()[0].replace("/", ".")
        jsonpath_expression = parse(f"$..{evaluated_key}")

        for policy in conf:
            policy_id = policy.get("type", {}).get("id")
            if policy_id == self.policy_type_id:
                if not policy.get("isEnabled"):
                    # let's check, if there is also an enabled one
                    continue

                matches = jsonpath_expression.find(policy)
                if matches and all(
                    isinstance(match.value, dict) or match.value == self.get_expected_value() for match in matches
                ):
                    return CheckResult.PASSED
                else:
                    return CheckResult.FAILED

        return CheckResult.FAILED

    def get_expected_value(self) -> str | bool | int:
        return True

    @abstractmethod
    def get_evaluated_keys(self) -> list[str]:
        pass
