from checkov.terraform.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_check import BaseResourceCheck


class ElasticsearchEncryption(BaseResourceCheck):
    def __init__(self):
        name = "Ensure all data stored in the Elasticsearch is securely encrypted at rest"
        id = "CKV_AWS_5"
        supported_resources = ['aws_elasticsearch_domain']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for encryption configuration at aws_elasticsearch_domain:
            https://www.terraform.io/docs/providers/aws/r/elasticsearch_domain.html
        :param conf: aws_elasticsearch_domain configuration
        :return: <CheckResult>
        """
        if "encrypt_at_rest" in conf.keys():
            if conf["encrypt_at_rest"][0]["enabled"][0]:
                return CheckResult.PASSED
        return CheckResult.FAILED


check = ElasticsearchEncryption()
