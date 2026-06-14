from checkov.common.models.consts import ANY_VALUE
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class SpannerDatabaseEncryptedWithCMK(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Spanner Database is encrypted with Customer Supplied Encryption Keys (CSEK)"
        id = "CKV_GCP_93"
        supported_resources = ['google_spanner_database']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        encryption_config = conf.get('encryption_config', [[]])[0]
        if isinstance(encryption_config, dict):
            if any(k in encryption_config for k in ['kms_key_name', 'kms_key_names']):
                return CheckResult.PASSED

        return CheckResult.FAILED

    def evaluated_keys(self):
        return ['encryption_config']


check = SpannerDatabaseEncryptedWithCMK()
