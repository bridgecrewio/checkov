from checkov.terraform.checks.resource.BaseResourceBooleanValueCheck import BaseResourceBooleanValueCheck
from checkov.terraform.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_check import BaseResourceCheck


class EBSSnapshotEncryption(BaseResourceBooleanValueCheck):
    def __init__(self):
        name = "Ensure all data stored in the EBS Snapshot is securely encrypted "
        id = "CKV_AWS_4"
        supported_resources = ['aws_ebs_snapshot']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "encrypted"


check = EBSSnapshotEncryption()
