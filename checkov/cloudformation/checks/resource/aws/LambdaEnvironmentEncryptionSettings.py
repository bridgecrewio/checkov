from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck


class LambdaEnvironmentEncryptionSettings(BaseResourceCheck):
    def __init__(self):
        name = "Check encryption settings for Lambda environmental variable"
        id = "CKV_AWS_173"
        supported_resources = ['AWS::Lambda::Function']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        env_vars_in_use = False
        kms_in_use = False

        properties = conf.get('Properties')
        if properties is not None:
            env_config = properties.get('Environment')
            kms_config = properties.get('KmsKeyArn')

            if env_config is not None:
                env_vars_config = env_config.get('Variables', [])
                if len(env_vars_config) > 0:
                    env_vars_in_use = True

            if kms_config is not None:
                kms_in_use = True

        if env_vars_in_use and not kms_in_use:
            return CheckResult.FAILED
            
        return CheckResult.PASSED
		

check = LambdaEnvironmentEncryptionSettings()
