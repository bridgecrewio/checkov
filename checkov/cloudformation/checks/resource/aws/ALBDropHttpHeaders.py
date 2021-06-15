from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck


class ALBDropHttpHeaders(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that ALB drops HTTP headers"
        id = "CKV_AWS_131"
        supported_resources = ["AWS::ElasticLoadBalancingV2::LoadBalancer"]
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'Properties' in conf.keys():
            if 'SnapshotIdentifier' in conf['Properties'].keys() or 'SourceDBClusterIdentifier' in conf['Properties'].keys():
                return CheckResult.UNKNOWN
        return super().scan_resource_conf(conf)

    def get_inspected_key(self):
        return 'Properties/StorageEncrypted'


check = ALBDropHttpHeaders()
