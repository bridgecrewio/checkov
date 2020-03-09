from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck

class CloudfrontDistributionEncryption(BaseResourceCheck):
    def __init__(self):
        name = "Ensure cloudfront distribution ViewerProtocolPolicy is set to HTTPS"
        id = "CKV_AWS_34"
        supported_resources = ['AWS::CloudFront::Distribution']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for ViewerProtocolPolicy configuration at cloudfront distributions:
            https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cloudfront-distribution-cachebehavior.html
            https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cloudfront-distribution-defaultcachebehavior.html
        :param conf: cloudfront configuration
        :return: <CheckResult>
        """

        if 'Properties' in conf.keys():
            if 'DistributionConfig' in conf['Properties'].keys():
                if 'DefaultCacheBehavior' in conf['Properties']['DistributionConfig'].keys():
                    if 'ViewerProtocolPolicy' in conf['Properties']['DistributionConfig']['DefaultCacheBehavior'].keys():
                        if conf['Properties']['DistributionConfig']['DefaultCacheBehavior']['ViewerProtocolPolicy'] == 'allow-all':
                            return CheckResult.FAILED
                if 'CacheBehaviors' in conf['Properties']['DistributionConfig'].keys():
                    for behavior in range(len(conf['Properties']['DistributionConfig']['CacheBehaviors'])):
                        if 'ViewerProtocolPolicy' in conf['Properties']['DistributionConfig']['CacheBehaviors'][behavior].keys():
                            if conf['Properties']['DistributionConfig']['CacheBehaviors'][behavior]['ViewerProtocolPolicy'] == 'allow-all':
                                return CheckResult.FAILED
        return CheckResult.PASSED

check = CloudfrontDistributionEncryption()
