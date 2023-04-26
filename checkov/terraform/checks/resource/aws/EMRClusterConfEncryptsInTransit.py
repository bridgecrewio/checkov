
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class EMRClusterConfEncryptsInTransit(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Cluster security configuration encrypts InTransit"
        id = "CKV_AWS_351"
        supported_resources = ['aws_emr_security_configuration']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'configuration' not in conf:
            return CheckResult.SKIPPED
        configuration = conf['configuration'][0]
        if configuration.get("EncryptionConfiguration") \
                and isinstance(configuration.get("EncryptionConfiguration"), dict):
            config = configuration.get("EncryptionConfiguration")
            if config.get("EnableInTransitEncryption") and isinstance(config.get("EnableInTransitEncryption"), bool):
                return CheckResult.PASSED

        return CheckResult.FAILED


check = EMRClusterConfEncryptsInTransit()
