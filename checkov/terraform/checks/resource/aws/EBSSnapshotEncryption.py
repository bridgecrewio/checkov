from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class EBSSnapshotEncryption(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure all data stored in the EBS Snapshot is securely encrypted "
        id = "CKV_AWS_4"
        supported_resources = ['aws_ebs_snapshot']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "encrypted"


check = EBSSnapshotEncryption()
