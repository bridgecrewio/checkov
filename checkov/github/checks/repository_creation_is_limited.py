from __future__ import annotations

from typing import Any
from jsonpath_ng import parse

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.github.base_github_configuration_check import BaseGithubCheck
from checkov.github.schemas.organization import schema as org_schema
from checkov.json_doc.enums import BlockType


class GithubRepositoryCreationIsLimited(BaseGithubCheck):
    def __init__(self) -> None:
        name = "Ensure repository creation is limited to specific members"
        # see https://docs.github.com/en/rest/orgs/orgs?apiVersion=2022-11-28#update-an-organization
        # https://developer.github.com/changes/2019-12-03-internal-visibility-changes/
        # members_allowed_repository_creation_type is deprecated.
        id = "CKV_GITHUB_21"
        categories = (CheckCategories.SUPPLY_CHAIN,)
        super().__init__(
            id=id,
            name=name,
            categories=categories,
            supported_entities=["*"],
            block_type=BlockType.DOCUMENT
        )

    def scan_entity_conf(self, conf: dict[str, Any], entity_type: str) -> CheckResult | None:  # type:ignore[override]
        members_can_create_repositories = False
        found_parameters = set()
        if org_schema.validate(conf):
            for evaluated_key in self.get_evaluated_keys():
                jsonpath_expression = parse("$..{}".format(evaluated_key.replace("/", ".")))
                matches = jsonpath_expression.find(conf)
                if matches:
                    found_parameters.add(evaluated_key)
                    members_can_create_repositories |= matches[0].value
            if len(found_parameters) != 3 or members_can_create_repositories:
                return CheckResult.FAILED
            return CheckResult.PASSED
        return None

    def get_evaluated_keys(self) -> list[str]:
        return [
            "members_can_create_public_repositories",
            "members_can_create_private_repositories",
            "members_can_create_internal_repositories"
        ]


check = GithubRepositoryCreationIsLimited()
