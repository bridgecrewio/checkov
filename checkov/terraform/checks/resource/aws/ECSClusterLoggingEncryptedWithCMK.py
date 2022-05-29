from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class ECSClusterLoggingEncryptedWithCMK(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Cluster logging with CMK"
        id = "CKV_AWS_224"
        supported_resources = ['aws_ecs_cluster']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        configuration = conf.get("configuration")
        if configuration and isinstance(configuration[0], dict) and configuration[0].get('execute_command_configuration'):
            command_conf = configuration[0].get('execute_command_configuration')[0]
            if not command_conf.get('logging') == ['NONE']:
                if command_conf.get('kms_key_id'):
                    if command_conf.get('log_configuration'):
                        log_conf = command_conf.get('log_configuration')[0]
                        if log_conf.get('cloud_watch_encryption_enabled') == [True] or \
                                log_conf.get('s3_bucket_encryption_enabled') == [True]:
                            return CheckResult.PASSED
                    return CheckResult.FAILED
                else:
                    return CheckResult.FAILED

        return CheckResult.UNKNOWN


check = ECSClusterLoggingEncryptedWithCMK()
