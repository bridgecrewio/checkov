from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck

MAX_SESSION_DURATION = 3600  # 1 hour in seconds


class IAMRoleMaxSessionDuration(BaseResourceCheck):
    def __init__(self):
        name = "Ensure IAM role max session duration does not exceed 1 hour"
        id = "CKV_AWS_341"
        supported_resources = ["aws_iam_role"]
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
        Looks for max_session_duration in aws_iam_role resources.
        https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role

        The default value in AWS is 3600 seconds (1 hour).
        Allowing sessions longer than 1 hour increases the blast radius
        of a compromised credential.

        Pass: max_session_duration is not set (defaults to 3600) or is <= 3600
        Fail: max_session_duration is set to a value > 3600
        """
        max_session_duration = conf.get("max_session_duration")

        # not set — defaults to 3600, passes
        if not max_session_duration:
            return CheckResult.PASSED

        # handle list wrapping from Terraform parser
        if isinstance(max_session_duration, list):
            max_session_duration = max_session_duration[0]

        # skip if variable reference (can't evaluate at scan time)
        if not isinstance(max_session_duration, int):
            return CheckResult.UNKNOWN

        if max_session_duration <= MAX_SESSION_DURATION:
            return CheckResult.PASSED

        return CheckResult.FAILED


scanner = IAMRoleMaxSessionDuration()
