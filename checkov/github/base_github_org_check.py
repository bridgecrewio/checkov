from __future__ import annotations

from abc import abstractmethod
from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.common.util.json_utils import get_jsonpath_from_evaluated_key
from checkov.github.base_github_configuration_check import BaseGithubCheck
from checkov.github.schemas.organization import schema as org_schema
from checkov.json_doc.enums import BlockType


class BaseOrganizationCheck(BaseGithubCheck):
    def __init__(self, id: str, name: str, missing_attribute_result: CheckResult = CheckResult.PASSED) -> None:
        categories = (CheckCategories.SUPPLY_CHAIN,)
        super().__init__(
            id=id,
            name=name,
            categories=categories,
            supported_entities=("*",),
            block_type=BlockType.DOCUMENT,
        )
        self.missing_attribute_result = missing_attribute_result

    def scan_entity_conf(self, conf: dict[str, Any], entity_type: str) -> CheckResult:  # type:ignore[override]
        ckv_metadata, conf = self.resolve_ckv_metadata_conf(conf=conf)
        if 'org_metadata' in ckv_metadata.get('file_name', ''):
            if org_schema.validate(conf):
                evaluated_key = self.get_evaluated_keys()[0]
                jsonpath_expression = get_jsonpath_from_evaluated_key(evaluated_key)
                matches = jsonpath_expression.find(conf)
                if matches:
                    if matches[0].value in self.get_allowed_values():
                        return CheckResult.PASSED
                    return CheckResult.FAILED
                return self.missing_attribute_result
        return CheckResult.UNKNOWN

    @abstractmethod
    def get_evaluated_keys(self) -> list[str]:
        pass

    @abstractmethod
    def get_allowed_values(self) -> list[Any]:
        pass
