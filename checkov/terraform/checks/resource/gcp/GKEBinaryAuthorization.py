from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class GKEBinaryAuthorization(BaseResourceCheck):
    def __init__(self):
        name = "Ensure use of Binary Authorization"
        id = "CKV_GCP_66"
        supported_resources = ['google_container_cluster']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'binary_authorization' in conf.keys():
            binary_authorization = conf["binary_authorization"][0]
            if isinstance(binary_authorization, dict) and 'evaluation_mode' in binary_authorization:
                # Google provider version >= v4.31.0
                if binary_authorization.get("evaluation_mode") == ["PROJECT_SINGLETON_POLICY_ENFORCE"]:
                    return CheckResult.PASSED
                # Google provider version v4.29.0 and v4.30.0
                elif binary_authorization.get("evaluation_mode") == [True]:
                    return CheckResult.PASSED
        # Google provider version <= v4.28.0
        if conf.get("enable_binary_authorization") == [True]:
            return CheckResult.PASSED
        return CheckResult.FAILED

    def get_evaluated_keys(self):
        return ['binary_authorization', 'enable_binary_authorization']


check = GKEBinaryAuthorization()
