from checkov.terraform.models.enums import ScanResult, ScanCategories
from checkov.terraform.checks.resource.base_check import BaseResourceCheck


class ElasticsearchNodeToNodeEncryption(BaseResourceCheck):
    def __init__(self):
        name = "Ensure all Elasticsearch has node-to-node encryption enabled"
        scan_id = "BC_AWS_ES_2"
        supported_resources = ['aws_elasticsearch_domain']
        categories = [ScanCategories.ENCRYPTION]
        super().__init__(name=name, scan_id=scan_id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for node to node encryption configuration at aws_elasticsearch_domain:
            https://www.terraform.io/docs/providers/aws/r/elasticsearch_domain.html
        :param conf: aws_elasticsearch_domain configuration
        :return: <ScanResult>
        """
        if "cluster_config" in conf.keys():

            instance_count = conf["cluster_config"][0]["instance_count"][0]
            if isinstance(instance_count,int):
                if instance_count > 1:
                    if "node_to_node_encryption" in conf.keys():
                        if conf["node_to_node_encryption"][0]["enabled"][0]:
                            return ScanResult.SUCCESS
                        else:
                            return ScanResult.FAILURE
                    else:
                        return ScanResult.FAILURE
                else:
                    return ScanResult.SUCCESS
            else:
                return ScanResult.UNKNOWN
        return ScanResult.SUCCESS


scanner = ElasticsearchNodeToNodeEncryption()
