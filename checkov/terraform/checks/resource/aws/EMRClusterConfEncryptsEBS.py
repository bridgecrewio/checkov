
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class EMRClusterConfEncryptsEBS(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Cluster security configuration encrypts ebs disks"
        id = "CKV_AWS_350"
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
            if config.get("EnableAtRestEncryption") and isinstance(config.get("EnableAtRestEncryption"), bool):
                if config.get("AtRestEncryptionConfiguration") \
                        and isinstance(config.get("AtRestEncryptionConfiguration"), dict):
                    atrest = config.get("AtRestEncryptionConfiguration")
                    if atrest.get("LocalDiskEncryptionConfiguration") \
                            and isinstance(atrest.get("LocalDiskEncryptionConfiguration"), dict):
                        ebs = atrest.get("LocalDiskEncryptionConfiguration")
                        if ebs.get("EnableEbsEncryption"):
                            return CheckResult.PASSED

        return CheckResult.FAILED


check = EMRClusterConfEncryptsEBS()
