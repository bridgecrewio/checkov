from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class AppLoadBalancerTLS12(BaseResourceCheck):
    def __init__(self):
        name = "Ensure that load balancer is using TLS 1.2"
        id = "CKV_AWS_103"
        supported_resources = ['aws_lb_listener']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        key="protocol"
        if key in conf.keys():
            if conf[key] == ["HTTPS"]:
              # Only interested in HTTPS listeners
                policy="ssl_policy"
                if policy in conf.keys():
                  name=str(conf[policy]).strip("['']") 
                  if name.startswith("ELBSecurityPolicy-FS-1-2") or name.startswith("ELBSecurityPolicy-TLS-1-2"):
                    return CheckResult.PASSED
                  else:
                    return CheckResult.FAILED
                else:
                  return CheckResult.FAILED
            else:
                for action in conf.get('default_action',[]):
                    for redirect in action.get('redirect',[]):
                        if redirect.get('protocol',[]) == ["HTTPS"]:
                            return CheckResult.PASSED
                return CheckResult.FAILED
        else:
            return CheckResult.FAILED


check = AppLoadBalancerTLS12()
