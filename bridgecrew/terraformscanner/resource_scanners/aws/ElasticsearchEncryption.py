from bridgecrew.terraformscanner.models.enums import ScanResult, ScanCategories
from bridgecrew.terraformscanner.resource_scanner import ResourceScanner


class ElasticsearchEncryption(ResourceScanner):
    def __init__(self):
        name = "Ensure all data stored in the Elasticsearch is securely encrypted at rest"
        scan_id = "BC_AWS_ES_1"
        supported_resources = ['aws_elasticsearch_domain']
        categories = [ScanCategories.ENCRYPTION]
        super().__init__(name=name, scan_id=scan_id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for encryption configuration at aws_elasticsearch_domain:
            https://www.terraform.io/docs/providers/aws/r/elasticsearch_domain.html
        :param conf: aws_elasticsearch_domain configuration
        :return: <ScanResult>
        """
        if "encrypt_at_rest" in conf.keys():
            if conf["encrypt_at_rest"][0]["enabled"][0]:
                return ScanResult.SUCCESS
        return ScanResult.FAILURE


scanner = ElasticsearchEncryption()
