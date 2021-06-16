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
        # alb is default loadbalancer type if not explicitly set
        alb = True

        if 'Properties' in conf.keys():
            properties = conf['Properties']
            if 'Type' in properties.keys():
                lb_type = properties['Type']
                if lb_type != 'application':
                    alb = False

           # If lb is alb then drop headers must be present and true 
            if alb == True:
                if 'LoadBalancerAttributes' in properties.keys():
                    lb_attributes = properties['LoadBalancerAttributes']
                    if isinstance(lb_attributes, list):
                        for item in lb_attributes:
                            if 'Key' in item.keys() and 'Value' in item.keys():
                                key = item['Key']
                                value = item['Value']
                                if key == 'routing.http.drop_invalid_header_fields.enabled' and value == "true":
                                    return CheckResult.PASSED
                return CheckResult.FAILED

        return CheckResult.PASSED


check = ALBDropHttpHeaders()
