from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck


class ELBv2AccessLogs(BaseResourceCheck):
    def __init__(self):
        name = "Ensure the ELBv2 (Application/Network) has access logging enabled"
        id = "CKV_AWS_91"
        supported_resources = ['AWS::ElasticLoadBalancingV2::LoadBalancer']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'Properties' in conf.keys():
            self.evaluated_keys = ['Properties']
            if 'LoadBalancerAttributes' in conf['Properties'].keys():
                self.evaluated_keys = ['Properties/LoadBalancerAttributes']
                if isinstance(conf['Properties']['LoadBalancerAttributes'], list):
                    for item in conf['Properties']['LoadBalancerAttributes']:
                        if 'Key' in item.keys() and 'Value' in item.keys():
                            if item['Key'] == "access_logs.s3.enabled":
                                value = item['Value']
                                if isinstance(value, bool):
                                    value = str(value).lower()
                                if value == "true":
                                    return CheckResult.PASSED
        return CheckResult.FAILED


check = ELBv2AccessLogs()
