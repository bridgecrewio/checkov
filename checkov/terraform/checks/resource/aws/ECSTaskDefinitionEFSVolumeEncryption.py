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
        self.evaluated_keys = ['volume']
        if 'volume' in conf.keys():
            for volume_idx, volume in enumerate(conf['volume']):
                if isinstance(volume, dict) and 'efs_volume_configuration' in volume:
                    for efs_idx, efs in enumerate(volume['efs_volume_configuration']):
                        if isinstance(efs, dict):
                            self.evaluated_keys = [f'volume/[{volume_idx}]/efs_volume_configuration/[{efs_idx}]']
                            if 'transit_encryption' in efs and efs['transit_encryption'] == ['ENABLED']:
                                return CheckResult.PASSED
                            return CheckResult.FAILED
        return CheckResult.PASSED


check = ECSTaskDefinitionEFSVolumeEncryption()
