from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import \
    BaseResourceCheck


class TKEPublicIpAssigned(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Tencent Cloud TKE cluster is not assigned a public IP address"
        id = "CKV_TC_7"
        supported_resources = ['tencentcloud_kubernetes_cluster']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf) -> CheckResult:
        if conf.get("master_config"):
            for mc in conf["master_config"]:
                if mc.get("public_ip_assigned") and mc["public_ip_assigned"][0]:
                    return CheckResult.FAILED
                if mc.get("public_ip_assigned") is None and mc.get("internet_max_bandwidth_out") and mc["internet_max_bandwidth_out"][0] > 0:
                    return CheckResult.FAILED

        if conf.get("worker_config"):
            for mc in conf["worker_config"]:
                if mc.get("public_ip_assigned") and mc["public_ip_assigned"][0]:
                    return CheckResult.FAILED
                if mc.get("public_ip_assigned") is None and mc.get("internet_max_bandwidth_out") and mc["internet_max_bandwidth_out"][0] > 0:
                    return CheckResult.FAILED
        return CheckResult.PASSED


check = TKEPublicIpAssigned()
