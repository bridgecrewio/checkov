from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.util.type_forcers import force_list
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class AppLoadBalancerTLS12(BaseResourceCheck):
    def __init__(self):
        name = "Ensure that load balancer is using TLS 1.2"
        id = "CKV_AWS_103"
        supported_resources = ["aws_lb_listener"]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_resources=supported_resources,
        )

    def scan_resource_conf(self, conf):
        key = "protocol"
        self.evaluated_keys = [key]
        if key in conf.keys():
            if conf[key] in (["HTTPS"], ["TLS"]):
                # Only interested in HTTPS & TLS listeners
                policy = "ssl_policy"
                if policy in conf.keys():
                    self.evaluated_keys.append(policy)
                    name = str(conf[policy]).strip("['']")
                    if name.startswith("ELBSecurityPolicy-FS-1-2") or name.startswith("ELBSecurityPolicy-TLS-1-2"):
                        return CheckResult.PASSED
                return CheckResult.FAILED
            elif conf[key] in (["TCP"], ["UDP"], ["TCP_UDP"]):
                return CheckResult.PASSED
            for idx_action, action in enumerate(conf.get("default_action", [])):
                redirects = action.get("redirect", [])
                for idx_redirect, redirect in enumerate(force_list(redirects)):
                    if redirect.get("protocol", []) == ["HTTPS"]:
                        redirect_index = f"[{idx_redirect}]/" if isinstance(redirects, list) else ""
                        self.evaluated_keys.append(f'default_action/[{idx_action}]/redirect/{redirect_index}protocol')
                        return CheckResult.PASSED
        return CheckResult.FAILED


check = AppLoadBalancerTLS12()
