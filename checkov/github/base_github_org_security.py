from abc import abstractmethod

from jsonpath_ng import parse

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.github.base_github_configuration_check import BaseGithubCheck
from checkov.github.schemas.org_security import schema as org_security_schema
from checkov.json_doc.enums import BlockType


class OrgSecurity(BaseGithubCheck):
    def __init__(self, id, name):
        categories = [CheckCategories.SUPPLY_CHAIN]
        super().__init__(
            id=id,
            name=name,
            categories=categories,
            supported_entities=["*"],
            block_type=BlockType.DOCUMENT
        )

    def scan_entity_conf(self, conf):
        if org_security_schema.validate(conf):
            jsonpath_expression = parse("$..{}".format(self.get_evaluated_keys()[0].replace("/", ".")))
            if all(match.value == self.get_expected_value() for match in jsonpath_expression.find(conf)):
                return CheckResult.PASSED
            else:
                return CheckResult.FAILED

    def get_expected_value(self):
        return True

    @abstractmethod
    def get_evaluated_keys(self):
        pass
