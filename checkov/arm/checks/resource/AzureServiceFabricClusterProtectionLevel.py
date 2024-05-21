from typing import Dict, List, Any
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.common.util.type_forcers import force_list
from checkov.arm.base_resource_check import BaseResourceCheck


class AzureServiceFabricClusterProtectionLevel(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensures that Service Fabric use three levels of protection available"
        id = "CKV_AZURE_125"
        supported_resources = ('Microsoft.ServiceFabric/clusters',)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        self.evaluated_keys = 'fabricSettings'
        settings_conf = force_list(conf.get('properties', {}).get('fabricSettings', []))
        for setting in settings_conf:
            if setting and setting.get('name') == 'Security':
                params = setting.get('parameters', [{}])[0]
                if params.get('name') == 'ClusterProtectionLevel' and params.get('value') == 'EncryptAndSign':
                    index = settings_conf.index(setting)
                    self.evaluated_keys = [f'fabricSettings/{index}/parameters/name',
                                           f'fabricSettings/{index}/parameters/value']
                    return CheckResult.PASSED
        return CheckResult.FAILED


check = AzureServiceFabricClusterProtectionLevel()
