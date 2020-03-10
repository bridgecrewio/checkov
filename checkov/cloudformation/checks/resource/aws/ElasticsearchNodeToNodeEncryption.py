from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck


class ElasticsearchNodeToNodeEncryption(BaseResourceCheck):
    def __init__(self):
        name = "Ensure all Elasticsearch has node-to-node encryption enabled"
        id = "CKV_AWS_6"
        supported_resources = ['AWS::Elasticsearch::Domain']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for node to node encryption configuration at aws_elasticsearch_domain:
            https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticsearch-domain.html
        :param conf: aws_elasticsearch_domain configuration
        :return: <CheckResult>
        """
        if 'Properties' in conf.keys():
            if 'NodeToNodeEncryptionOptions' in conf['Properties'].keys():
                if 'Enabled' in conf['Properties']['NodeToNodeEncryptionOptions'].keys():
                    if conf['Properties']['NodeToNodeEncryptionOptions']['Enabled']:
                        return CheckResult.PASSED
        return CheckResult.FAILED

check = ElasticsearchNodeToNodeEncryption()
