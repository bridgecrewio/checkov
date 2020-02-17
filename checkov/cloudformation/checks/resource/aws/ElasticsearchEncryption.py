from checkov.terraform.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_check import BaseResourceCheck


class ElasticsearchEncryption(BaseResourceCheck):
    def __init__(self):
        name = "Ensure all data stored in the Elasticsearch is securely encrypted at rest"
        id = "CKV_AWS_5"
        supported_resources = ['AWS::Elasticsearch::Domain']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for encryption configuration at aws_elasticsearch_domain:
            https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticsearch-domain.html
        :param conf: aws_elasticsearch_domain configuration
        :return: <CheckResult>
        """
        if conf['Type'] == 'AWS::Elasticsearch::Domain':
            if 'Properties' in conf.keys():
                if 'EncryptionAtRestOptions' in conf['Properties'].keys():
                    if 'Enabled' in conf['Properties']['EncryptionAtRestOptions'].keys():
                        if conf['Properties']['EncryptionAtRestOptions']['Enabled']:
                            return CheckResult.PASSED
        return CheckResult.FAILED

check = ElasticsearchEncryption()
