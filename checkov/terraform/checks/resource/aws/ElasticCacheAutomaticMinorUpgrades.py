from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class ElasticCacheAutomaticMinorUpgrades(BaseResourceValueCheck):
    def __init__(self):
        """
        NIST.800-53.r5 SI-2, NIST.800-53.r5 SI-2(2), NIST.800-53.r5 SI-2(4), NIST.800-53.r5 SI-2(5)
        ElastiCache for Redis cache clusters should have auto minor version upgrades enabled
        """
        name = "Ensure ElastiCache for Redis cache clusters have auto minor version upgrades enabled"
        id = "CKV_AWS_322"
        supported_resources = ["aws_elasticache_cluster"]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_resources=supported_resources,
            missing_block_result=CheckResult.PASSED
        )

    def scan_resource_conf(self, conf):
        if conf.get("engine") == ["memcached"]:
            return CheckResult.UNKNOWN

        return super().scan_resource_conf(conf)

    def get_inspected_key(self):
        return "auto_minor_version_upgrade"


check = ElasticCacheAutomaticMinorUpgrades()
