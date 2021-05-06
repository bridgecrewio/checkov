from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class WorkspaceUserVolumeEncrypted(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that Workspace user volumes are encrypted"
        id = "CKV_AWS_155"
        supported_resources = ['aws_workspaces_workspace']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'user_volume_encryption_enabled'

    def get_expected_value(self):
        return True


check = WorkspaceUserVolumeEncrypted()
