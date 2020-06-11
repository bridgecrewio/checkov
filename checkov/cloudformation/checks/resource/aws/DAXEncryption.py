from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class DAXEncryption(BaseResourceCheck):
    def __init__(self):
        name = "Ensure DAX is encrypted at rest (default is unencrypted)"
        id = "CKV_AWS_47"
        supported_resources = ['AWS::DAX::Cluster']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
        Looks for SSESpecification encryption configuration at aws_dax_cluster:
        https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dax-cluster.html
        :param conf: aws_dax_cluster configuration
        :return: <CheckResult>
        """
        if conf.get('Properties'):
            if conf['Properties'].get('SSESpecification'):
                sse_specs_conf = conf['Properties']['SSESpecification']
                if sse_specs_conf.get('SSEEnabled'):
                    return CheckResult.PASSED
        return CheckResult.FAILED


check = DAXEncryption()
