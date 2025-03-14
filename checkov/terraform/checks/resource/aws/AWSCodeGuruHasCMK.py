from typing import Dict, List, Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class AWSCodeGuruHasCMK(BaseResourceCheck):
    def __init__(self):
        # This is the full description of your check
        description = "Make sure that aws_codegurureviewer_repository_association has a CMK"

        # This is the Unique ID for your check
        id = "CKV_AWS_381"

        # These are the terraform objects supported by this check (ex: aws_iam_policy_document)
        supported_resources = ['aws_codegurureviewer_repository_association']

        # Valid CheckCategories are defined in checkov/common/models/enums.py
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=description, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        if 'kms_key_details' in conf:
            kms_key_details = conf['kms_key_details'][0]
            if 'encryption_option' in kms_key_details:
                encryption_option = kms_key_details['encryption_option'][0]
                if encryption_option == 'CUSTOMER_MANAGED_CMK':
                    return CheckResult.PASSED

        return CheckResult.FAILED

    def get_evaluated_keys(self) -> List[str]:
        return ['kms_key_details']


check = AWSCodeGuruHasCMK()
