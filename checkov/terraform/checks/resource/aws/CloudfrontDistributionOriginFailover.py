from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class CloudfrontDistributionOriginFailover(BaseResourceCheck):
    def __init__(self) -> None:
        """
        NIST.800-53.r5 CP-10, NIST.800-53.r5 SC-36, NIST.800-53.r5 SC-5(2), NIST.800-53.r5 SI-13(5)
        CloudFront distributions should have origin failover configured
        """
        name = "Ensure CloudFront distributions should have origin failover configured"
        id = "CKV_AWS_310"
        supported_resources = ('aws_cloudfront_distribution',)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        groups = conf.get("origin_group")
        if groups and isinstance(groups, list):
            for group in groups:
                if isinstance(group, dict) and group.get("failover_criteria"):
                    member = group.get("member")
                    if not member or len(member) < 2:
                        return CheckResult.FAILED
                else:
                    return CheckResult.FAILED
        else:
            return CheckResult.FAILED
        return CheckResult.PASSED


check = CloudfrontDistributionOriginFailover()
