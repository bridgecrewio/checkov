from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories, CheckResult


class AuroraEncryption(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure all data stored in Aurrora is securely encrypted at rest"
        id = "CKV_AWS_96"
        supported_resources = ['aws_rds_cluster']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        # https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-serverless.how-it-works.html#aurora-serverless.snapshots
        # If aurora serverless is used it is always encrypted
        key='engine_mode'
        if key in conf.keys():
            if conf[key] == ['serverless']:
                return CheckResult.PASSED
        return super().scan_resource_conf(conf)

    def get_inspected_key(self):
        return "storage_encrypted"


check = AuroraEncryption()
