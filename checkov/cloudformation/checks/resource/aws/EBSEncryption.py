from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck


class EBSEncryption(BaseResourceCheck):
    def __init__(self):
        name = "Ensure all data stored in the EBS is securely encrypted "
        id = "CKV_AWS_3"
        supported_resources = ['AWS::EC2::Volume']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for encryption configuration at ebs volume:
            https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ebs-volume.html
        :param conf: ebs_volume configuration
        :return: <CheckResult>
        """
        if 'Properties' in conf.keys():
            if 'Encrypted' in conf['Properties'].keys():
                if conf['Properties']['Encrypted'] == True:
                    return CheckResult.PASSED
        return CheckResult.FAILED

check = EBSEncryption()
