from __future__ import annotations

from typing import Any
from bc_jsonpath_ng import parse

from checkov.common.models.enums import CheckResult
from checkov.github.base_github_gha_check import BaseGHACheck
from checkov.github.schemas.organization import schema as org_schema


class GithubAccessWorkflowsMinimized(BaseGHACheck):
    def __init__(self) -> None:
        # see GHA access for more info
        # https://docs.github.com/en/organizations/managing-user-access-to-your-organizations-repositories/setting-base-permissions-for-an-organization
        # https://docs.github.com/en/organizations/managing-user-access-to-your-organizations-repositories/repository-roles-for-an-organization
        name = "Ensure access to the build process's triggering is minimized"
        id = "CKV_GITHUB_29"
        super().__init__(id=id, name=name)

    def scan_entity_conf(self, conf: dict[str, Any], entity_type: str) -> CheckResult | None:  # type:ignore[override]
        ckv_metadata, conf = self.resolve_ckv_metadata_conf(conf=conf)
        if self.is_gha_enabled(ckv_metadata=ckv_metadata):
            if 'org_metadata' in ckv_metadata.get('file_name', ''):
                if org_schema.validate(conf):
                    evaluated_key = self.get_evaluated_keys()[0].replace("/", ".")
                    jsonpath_expression = parse(f"$..{evaluated_key}")
                    matches = jsonpath_expression.find(conf)
                    if matches:
                        if matches[0].value in self.get_allowed_values():
                            return CheckResult.PASSED
                        return CheckResult.FAILED
                    return CheckResult.PASSED  # default is read
            return None

    def get_evaluated_keys(self) -> list[str]:
        return ["default_repository_permission"]

    @staticmethod
    def get_allowed_values() -> list[Any]:
        return ['read', None]


check = GithubAccessWorkflowsMinimized()
