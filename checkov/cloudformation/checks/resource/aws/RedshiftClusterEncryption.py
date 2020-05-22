from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck


class RedshiftClusterEncryption(BaseResourceCheck):
    def __init__(self):
        name = "Ensure all data stored in the Redshift cluster is securely encrypted at rest"
        id = "CKV_AWS_64"
        supported_resources = ['AWS::Redshift::Cluster']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for encryption configuration at Redshift cluster:
            https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html
        :param conf: AWS::Redshift::Cluster configuration
        :return: <CheckResult>
        """
        if 'Properties' in conf.keys():
            if 'Encrypted' in conf['Properties'].keys():
                if conf['Properties']['Encrypted'] == True:
                    return CheckResult.PASSED
        return CheckResult.FAILED

check = RedshiftClusterEncryption()
