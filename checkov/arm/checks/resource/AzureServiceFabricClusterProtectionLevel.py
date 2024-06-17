from typing import Dict, List, Any, Union
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.arm.base_resource_check import BaseResourceCheck
from checkov.common.util.type_forcers import force_list


class AzureServiceFabricClusterProtectionLevel(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensures that Service Fabric use three levels of protection available"
        id = "CKV_AZURE_125"
        supported_resources = ('Microsoft.ServiceFabric/clusters',)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        properties: Union[List[Any], Dict[str, Any]] = conf.get('properties', {})
        if not isinstance(properties, dict):
            self.evaluated_keys = ['properties']
            return CheckResult.FAILED

        settings_conf = force_list(properties.get('fabricSettings', []))
        if not isinstance(settings_conf, list):
            self.evaluated_keys = ['properties/fabricSettings']
            return CheckResult.FAILED

        for setting in settings_conf:
            if setting and isinstance(setting, dict) and setting.get('name') == 'Security':
                params = setting.get('parameters', [{}])
                if isinstance(params, list) and len(params) > 0 and isinstance(params[0], dict):
                    param = params[0]
                    if param.get('name') == 'ClusterProtectionLevel' and param.get('value') == 'EncryptAndSign':
                        index = settings_conf.index(setting)
                        self.evaluated_keys = [f'fabricSettings/{index}/parameters/name',
                                               f'fabricSettings/{index}/parameters/value']
                        return CheckResult.PASSED
                else:
                    self.evaluated_keys = [f'fabricSettings/{settings_conf.index(setting)}/parameters']
                    return CheckResult.FAILED

        self.evaluated_keys = ['fabricSettings']
        return CheckResult.FAILED


check = AzureServiceFabricClusterProtectionLevel()
