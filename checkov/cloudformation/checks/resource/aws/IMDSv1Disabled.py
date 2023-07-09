from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck


class IMDSv1Disabled(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Instance Metadata Service Version 1 is not enabled"
        id = "CKV_AWS_79"
        supported_resources = ['AWS::EC2::LaunchTemplate']
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        # IMDS can be disabled or IMDSv2 can be enabled
        if 'Properties' in conf.keys():
            properties = conf['Properties']
            if 'LaunchTemplateData' in properties.keys():
                launch_template_data = properties['LaunchTemplateData']
            if 'MetadataOptions' in launch_template_data.keys():
                metadata_options = launch_template_data['MetadataOptions']
                if 'HttpEndpoint' in metadata_options.keys():
                    if metadata_options['HttpEndpoint'] == "disabled":
                        return CheckResult.PASSED
                if 'HttpTokens' in metadata_options.keys():
                    if metadata_options['HttpTokens'] == "required":
                        return CheckResult.PASSED
        return CheckResult.FAILED


check = IMDSv1Disabled()
