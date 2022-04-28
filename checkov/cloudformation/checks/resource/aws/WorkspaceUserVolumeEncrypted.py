from checkov.common.models.enums import CheckCategories
from checkov.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck


class WorkspaceUserVolumeEncrypted(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that Workspace user volumes are encrypted"
        id = "CKV_AWS_155"
        supported_resources = ['AWS::WorkSpaces::Workspace']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'Properties/UserVolumeEncryptionEnabled'


check = WorkspaceUserVolumeEncrypted()
