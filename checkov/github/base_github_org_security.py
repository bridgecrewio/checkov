from __future__ import annotations

from abc import abstractmethod

from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.common.util.json_utils import get_jsonpath_from_evaluated_key
from checkov.github.base_github_configuration_check import BaseGithubCheck
from checkov.github.schemas.org_security import schema as org_security_schema
from checkov.json_doc.enums import BlockType


class OrgSecurity(BaseGithubCheck):
    def __init__(self, id: str, name: str) -> None:
        categories = [CheckCategories.SUPPLY_CHAIN]
        super().__init__(
            id=id,
            name=name,
            categories=categories,
            supported_entities=["*"],
            block_type=BlockType.DOCUMENT
        )

    def scan_entity_conf(self, conf: dict[str, Any], entity_type: str) -> CheckResult:
        if org_security_schema.validate(conf):
            evaluated_key = self.get_evaluated_keys()[0]
            jsonpath_expression = get_jsonpath_from_evaluated_key(evaluated_key)
            if all(match.value == self.get_expected_value() for match in jsonpath_expression.find(conf)):
                return CheckResult.PASSED
            else:
                return CheckResult.FAILED
        return CheckResult.UNKNOWN

    def get_expected_value(self) -> int | bool | str:
        return True

    @abstractmethod
    def get_evaluated_keys(self) -> list[str]:
        pass
