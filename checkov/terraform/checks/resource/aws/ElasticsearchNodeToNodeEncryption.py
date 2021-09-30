from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.util.type_forcers import force_int


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
        self.evaluated_keys = ['cluster_config']
        cluster_config = conf.get("cluster_config")
        if not cluster_config or not isinstance(cluster_config[0], dict):
            return CheckResult.PASSED
        if "instance_count" not in cluster_config[0]:
            return CheckResult.PASSED

        self.evaluated_keys = ['cluster_config/[0]/instance_count']
        instance_count = cluster_config[0]["instance_count"]
        if isinstance(instance_count, list):
            instance_count = instance_count[0]
            if not isinstance(instance_count, int):
                return CheckResult.UNKNOWN
        if not instance_count:
            return CheckResult.UNKNOWN
        if instance_count <= 1:
            return CheckResult.PASSED

        self.evaluated_keys.append('node_to_node_encryption/[0]/enabled')
        if "node_to_node_encryption" in conf.keys() and "enabled" in conf["node_to_node_encryption"][0]:
            n2n_enc_enabled = conf["node_to_node_encryption"][0]["enabled"]
            if isinstance(n2n_enc_enabled, list):
                n2n_enc_enabled = conf["node_to_node_encryption"][0]["enabled"][0]
            if not isinstance(n2n_enc_enabled, bool):
                return CheckResult.UNKNOWN
            if n2n_enc_enabled:
                return CheckResult.PASSED
        return CheckResult.FAILED


check = ElasticsearchNodeToNodeEncryption()
