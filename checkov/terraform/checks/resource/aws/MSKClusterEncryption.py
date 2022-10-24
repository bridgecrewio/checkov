from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from typing import List


class MSKClusterEncryption(BaseResourceCheck):
    def __init__(self):
        name = "Ensure MSK Cluster encryption in rest and transit is enabled"
        id = "CKV_AWS_81"
        supported_resources = ['aws_msk_cluster']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        # Note: As long as the 'encryption_info' block is specified, the cluster
        # will be encrypted at rest even if 'encryption_at_rest_kms_key_arn' is not specified
        # See https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/msk_cluster#encryption_at_rest_kms_key_arn
        if 'encryption_info' in conf.keys():
            encryption = conf['encryption_info'][0]
            if 'encryption_in_transit' in encryption:
                transit = encryption['encryption_in_transit'][0]
                if 'client_broker' in transit and transit['client_broker'][0] != 'TLS' or \
                        'in_cluster' in transit and transit['in_cluster'][0] is False:
                    return CheckResult.FAILED
            return CheckResult.PASSED
        return CheckResult.FAILED

    def get_evaluated_keys(self) -> List[str]:
        return ['encryption_info/[0]/encryption_in_transit/[0]/client_broker',
                'encryption_info/[0]/encryption_in_transit/[0]/in_cluster']


check = MSKClusterEncryption()
