from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck


class ALBDropHttpHeaders(BaseResourceCheck):

    def __init__(self):
        name = "Ensure that ALB drops HTTP headers"
        id = "CKV_AWS_131"
        supported_resources = ["AWS::ElasticLoadBalancingV2::LoadBalancer"]
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'Properties' in conf.keys():
            properties = conf['Properties']
            if 'Type' in properties.keys():
                lb_type = properties['Type']
                if lb_type == 'application':
                    if 'LoadBalancerAttributes' in properties.keys():
                        lb_attributes = properties['LoadBalancerAttributes']
                        if isinstance(lb_attributes, list):
                            for item in lb_attributes:
                                print item
        return CheckResult.PASSED


check = ALBDropHttpHeaders()
