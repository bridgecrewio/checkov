from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories
from typing import Any
from checkov.common.models.consts import ANY_VALUE


class EFSAccessUserIdentity(BaseResourceValueCheck):
    def __init__(self):
        """
        NIST.800-53.r5 AC-6(2)
        EFS access points should enforce a user identity
        """
        name = "EFS access points should enforce a user identity"
        id = "CKV_AWS_330"
        supported_resources = ['aws_efs_access_point']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "posix_user/[0]/gid"

    def get_expected_value(self) -> Any:
        return ANY_VALUE


check = EFSAccessUserIdentity()
