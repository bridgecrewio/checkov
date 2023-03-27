from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceCheck
from typing import List


class CodebuildHasLogs(BaseResourceCheck):
    def __init__(self) -> None:
        """
        NIST.800-53.r5 AC-2(12), NIST.800-53.r5 AC-2(4), NIST.800-53.r5 AC-4(26), NIST.800-53.r5 AC-6(9),
        NIST.800-53.r5 AU-10, NIST.800-53.r5 AU-12, NIST.800-53.r5 AU-2, NIST.800-53.r5 AU-3, NIST.800-53.r5 AU-6(3),
        NIST.800-53.r5 AU-6(4), NIST.800-53.r5 AU-9(7), NIST.800-53.r5 CA-7, NIST.800-53.r5 SC-7(9),
        NIST.800-53.r5 SI-3(8), NIST.800-53.r5 SI-4, NIST.800-53.r5 SI-4(20), NIST.800-53.r5 SI-7(8)
        CodeBuild project environments should have a logging configuration
        """
        name = "Ensure CodeBuild project environments have a logging configuration"
        id = "CKV_AWS_314"
        supported_resources = ('aws_codebuild_project',)
        categories = (CheckCategories.LOGGING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        logs_config = conf.get('logs_config')
        if logs_config and isinstance(logs_config, list):
            logs = logs_config[0]
            if isinstance(logs, dict):
                if logs.get("cloudwatch_logs") or logs.get("s3_logs"):
                    return CheckResult.PASSED
        return CheckResult.FAILED

    def get_evaluated_keys(self) -> List[str]:
        return ['enabled_cloudwatch_logs_exports']


check = CodebuildHasLogs()
