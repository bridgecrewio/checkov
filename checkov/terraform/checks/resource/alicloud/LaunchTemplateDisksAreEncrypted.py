from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class LaunchTemplateDisksAreEncrypted(BaseResourceCheck):
    def __init__(self):
        name = "Ensure launch template data disks are encrypted"
        id = "CKV_ALI_32"
        supported_resources = ['alicloud_ecs_launch_template']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        data_disks = conf.get("data_disks")
        if data_disks and isinstance(data_disks, list):
            for disk in data_disks:
                if disk.get('encrypted') != [True]:
                    return CheckResult.FAILED
        return CheckResult.PASSED


check = LaunchTemplateDisksAreEncrypted()
