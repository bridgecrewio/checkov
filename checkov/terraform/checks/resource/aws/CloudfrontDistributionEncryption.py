from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class CloudfrontDistributionEncryption(BaseResourceCheck):
    def __init__(self):
        name = "Ensure cloudfront distribution ViewerProtocolPolicy is set to HTTPS"
        id = "CKV_AWS_34"
        supported_resources = ['aws_cloudfront_distribution']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for ViewerProtocolPolicy configuration at cloudfront distributions:
            https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution.html#viewer_protocol_policy
        :param conf: cloudfront configuration
        :return: <CheckResult>
        """
        if "default_cache_behavior" in conf.keys():
            self.evaluated_keys = 'default_cache_behavior/[0]/viewer_protocol_policy'
            if isinstance(conf["default_cache_behavior"][0], dict):
                default_viewer_policy = conf["default_cache_behavior"][0]["viewer_protocol_policy"]
                if default_viewer_policy and default_viewer_policy[0] == "allow-all":
                    return CheckResult.FAILED
        if "ordered_cache_behavior" in conf.keys():
            for behavior in conf["ordered_cache_behavior"]:
                if isinstance(behavior, dict):
                    # behavior which is a string will return PASSED
                    if behavior["viewer_protocol_policy"][0] == "allow-all":
                        self.evaluated_keys = f'ordered_cache_behavior/[{conf["ordered_cache_behavior"].index(behavior)}]/viewer_protocol_policy'
                        return CheckResult.FAILED
        return CheckResult.PASSED


check = CloudfrontDistributionEncryption()
