from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class ElasticsearchNodeToNodeEncryption(BaseResourceCheck):
    def __init__(self):
        name = "Ensure all Elasticsearch has node-to-node encryption enabled"
        id = "CKV_AWS_6"
        supported_resources = ['aws_elasticsearch_domain']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for node to node encryption configuration at aws_elasticsearch_domain:
            https://www.terraform.io/docs/providers/aws/r/elasticsearch_domain.html
        :param conf: aws_elasticsearch_domain configuration
        :return: <CheckResult>
        """
        if "cluster_config" in conf.keys():
            cluster_config = conf["cluster_config"][0]
            if isinstance(cluster_config, dict):
                if "instance_count" not in cluster_config:
                    return CheckResult.PASSED
                self.evaluated_keys = ['cluster_config/[0]/instance_count']
                instance_count = cluster_config["instance_count"]
                if isinstance(instance_count, int):
                    if instance_count > 1:
                        self.evaluated_keys.append('node_to_node_encryption/[0]/enabled')
                        if "node_to_node_encryption" in conf.keys() and "enabled" in conf["node_to_node_encryption"][0]:
                            if conf["node_to_node_encryption"][0]["enabled"]:
                                return CheckResult.PASSED
                        return CheckResult.FAILED
                    return CheckResult.PASSED
                return CheckResult.UNKNOWN
        return CheckResult.PASSED


check = ElasticsearchNodeToNodeEncryption()
