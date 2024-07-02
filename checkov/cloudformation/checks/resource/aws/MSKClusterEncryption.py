from typing import Any, List

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck


class MSKClusterEncryption(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure MSK Cluster encryption in rest and transit is enabled"
        id = "CKV_AWS_81"
        supported_resources = ['AWS::MSK::Cluster']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf) -> Any:
        # Note: As long as the 'EncryptionInfo' block is specified, the cluster
        # will be encrypted at rest even if 'DataVolumeKMSKeyId' is not specified
        if 'Properties' in conf.keys():
            if 'EncryptionInfo' in conf['Properties'].keys():
                encryption = conf['Properties']['EncryptionInfo']
                if 'EncryptionInTransit' in encryption:
                    transit = encryption['EncryptionInTransit']
                    if 'ClientBroker' in transit and transit['ClientBroker'] != 'TLS' or \
                            'InCluster' in transit and transit['InCluster'] is False:
                        return CheckResult.FAILED
                return CheckResult.PASSED
        return CheckResult.FAILED

    def get_evaluated_keys(self) -> List[str]:
        return ['Properties/EncryptionInfo/EncryptionInTransit/ClientBroker',
                'Properties/EncryptionInfo/EncryptionInTransit/InCluster']


check = MSKClusterEncryption()
