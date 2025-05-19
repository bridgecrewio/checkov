from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.consts import ANY_VALUE


class RDSInstancePerfInsightsEncryptionWithCMK(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure RDS Performance Insights are encrypted using KMS CMKs"
        id = "CKV_AWS_354"
        supported_resources = ['aws_rds_cluster_instance', 'aws_db_instance']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf) -> CheckResult:
        if 'performance_insights_enabled' in conf and conf['performance_insights_enabled'][0]:
            if 'performance_insights_kms_key_id' not in conf or not conf['performance_insights_kms_key_id']:
                return CheckResult.FAILED
        return CheckResult.PASSED

    def get_inspected_key(self) -> str:
        return 'performance_insights_kms_key_id'

    def get_expected_value(self) -> Any:
        return ANY_VALUE


check = RDSInstancePerfInsightsEncryptionWithCMK()
