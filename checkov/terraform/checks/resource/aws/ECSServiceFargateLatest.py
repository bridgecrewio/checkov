from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class ECSServiceFargateLatest(BaseResourceCheck):
    def __init__(self):
        """
        NIST.800-53.r5 SI-2, NIST.800-53.r5 SI-2(2), NIST.800-53.r5 SI-2(4), NIST.800-53.r5 SI-2(5)
        ECS Fargate services should run on the latest Fargate platform version
        """
        name = "Ensure ECS Fargate services run on the latest Fargate platform version"
        id = "CKV_AWS_332"
        supported_resources = ["aws_ecs_service"]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_resources=supported_resources,
        )

    def scan_resource_conf(self, conf):
        if 'launch_type' in conf.keys() and isinstance(conf.get("launch_type"), list):
            launch_type = conf.get("launch_type")[0]
            if launch_type == "FARGATE":
                if conf.get("platform_version") and isinstance(conf.get("platform_version"), list):
                    version = conf.get("platform_version")[0]
                    if version == "LATEST":
                        return CheckResult.PASSED
                    return CheckResult.FAILED
                return CheckResult.PASSED
        return CheckResult.UNKNOWN


check = ECSServiceFargateLatest()
