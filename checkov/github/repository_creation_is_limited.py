from __future__ import annotations

from abc import abstractmethod
from typing import Any
from jsonpath_ng import parse

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.github.base_github_configuration_check import BaseGithubCheck
from checkov.github.schemas.organization import schema as org_schema
from checkov.json_doc.enums import BlockType


class RepositoryCreationIsLimited(BaseGithubCheck):
    def __init__(self, id: str, name: str) -> None:
        # see https://docs.github.com/en/rest/orgs/orgs?apiVersion=2022-11-28#update-an-organization
        # https://developer.github.com/changes/2019-12-03-internal-visibility-changes/
        # members_allowed_repository_creation_type is deprecated.
        categories = (CheckCategories.SUPPLY_CHAIN,)
        super().__init__(
            id=id,
            name=name,
            categories=categories,
            supported_entities=("*",),
            block_type=BlockType.DOCUMENT
        )

    def scan_entity_conf(self, conf: dict[str, Any], entity_type: str) -> CheckResult | None:  # type:ignore[override]
        if org_schema.validate(conf):
            evaluated_key = self.get_evaluated_keys()[0]
            jsonpath_expression = parse("$..{}".format(evaluated_key.replace("/", ".")))
            matches = jsonpath_expression.find(conf)
            if matches and not matches[0].value:
                return CheckResult.PASSED
            # default value for all 3 public, internal and private is true.
            return CheckResult.FAILED
        return None

    @abstractmethod
    def get_evaluated_keys(self) -> list[str]:
        pass
