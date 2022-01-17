from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.gitlab.base_gitlab_configuration_check import BaseGitlabCheck
from checkov.gitlab.schemas.groups import schema
from checkov.json_doc.enums import BlockType


class GroupsTwoFactorAuthentication(BaseGitlabCheck):
    def __init__(self):
        name = "Ensure all Gitlab groups require two factor authentication"
        id = "CKV_GITLAB_2"
        categories = [CheckCategories.SUPPLY_CHAIN]
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_entities=["*"],
            block_type=BlockType.DOCUMENT
        )

    def scan_entity_conf(self, conf):
        if schema.validate(conf):
            for group in conf:
                if group.get("require_two_factor_authentication", False) is True:
                    return CheckResult.PASSED, conf
            return CheckResult.FAILED, conf


check = GroupsTwoFactorAuthentication()
