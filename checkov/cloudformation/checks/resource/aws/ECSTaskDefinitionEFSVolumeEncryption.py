from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck


class ECSTaskDefinitionEFSVolumeEncryption(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Encryption in transit is enabled for EFS volumes in ECS Task definitions"
        id = "CKV_AWS_97"
        supported_resources = ['AWS::ECS::TaskDefinition']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'Properties' in conf.keys():
            if 'Volumes' in conf['Properties'].keys():
                volumes = conf['Properties']['Volumes']
                if isinstance(volumes, list):
                    for volume in volumes:
                        if 'EFSVolumeConfiguration' in volume.keys():
                            if 'TransitEncryption' in volume['EFSVolumeConfiguration'].keys():
                                if volume['EFSVolumeConfiguration']['TransitEncryption'] == 'ENABLED':
                                    return CheckResult.PASSED
                                else:
                                    return CheckResult.FAILED
                            else:
                                return CheckResult.FAILED
        return CheckResult.PASSED

check = ECSTaskDefinitionEFSVolumeEncryption()
