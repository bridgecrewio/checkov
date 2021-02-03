from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class ECSTaskDefinitionEFSVolumeEncryption(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Encryption in transit is enabled for EFS volumes in ECS Task definitions"
        id = "CKV_AWS_97"
        supported_resources = ['aws_ecs_task_definition']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'volume' in conf.keys():
            volume_conf = conf['volume']
            for volume in volume_conf:
                if isinstance(volume, dict) and 'efs_volume_configuration' in volume:
                    efs_conf = volume['efs_volume_configuration']
                    for efs in efs_conf:
                        if isinstance(efs, dict):
                            if 'transit_encryption' in efs and efs['transit_encryption'] == ['ENABLED']:
                                return CheckResult.PASSED
                            else:
                                return CheckResult.FAILED
        return CheckResult.PASSED


check = ECSTaskDefinitionEFSVolumeEncryption()
