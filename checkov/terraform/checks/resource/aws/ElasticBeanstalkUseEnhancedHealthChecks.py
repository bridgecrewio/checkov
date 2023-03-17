from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class ElasticBeanstalkUseEnhancedHealthChecks(BaseResourceCheck):
    def __init__(self):
        """
        NIST.800-53.r5 CA-7, NIST.800-53.r5 SI-2
        Elastic Beanstalk environments should have enhanced health reporting enabled
        """
        name = "Ensure E"
        id = "CKV_AWS_312"
        supported_resources = ['aws_elastic_beanstalk_environment']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if conf.get("setting"):
            settings = conf.get("setting")
            if isinstance(settings[0], list):
                settings = settings[0]
            for setting in settings:
                if isinstance(setting.get("namespace"), list) and \
                        setting.get("namespace")[0] == "aws:elasticbeanstalk:healthreporting:system":
                    if isinstance(setting.get("value"), list) and setting.get("value")[0] == "enhanced":
                        return CheckResult.PASSED
        return CheckResult.FAILED


check = ElasticBeanstalkUseEnhancedHealthChecks()
