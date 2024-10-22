from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceCheck
from checkov.common.models.enums import CheckCategories, CheckResult


class CloudFunctionsShouldNotBePublic(BaseResourceCheck):
    def __init__(self):
        name = "Cloud functions should not be public"
        id = "CKV_GCP_107"
        supported_resources = [
            "google_cloudfunctions_function_iam_member",
            "google_cloudfunctions_function_iam_binding",
            "google_cloudfunctions2_function_iam_member",
            "google_cloudfunctions2_function_iam_binding"
        ]
        categories = [CheckCategories.APPLICATION_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf) -> CheckResult:
        if conf.get("member") and isinstance(conf.get("member"), list):
            if conf.get("member") == ["allUsers"]:
                return CheckResult.FAILED
            return CheckResult.PASSED
        if conf.get("members") and isinstance(conf.get("members")[0], list):
            if "allUsers" in conf.get("members")[0]:
                return CheckResult.FAILED
            return CheckResult.PASSED
        return CheckResult.UNKNOWN


check = CloudFunctionsShouldNotBePublic()
