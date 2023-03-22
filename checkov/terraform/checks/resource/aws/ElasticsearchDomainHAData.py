from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckCategories, CheckResult


class ElasticsearchDomainHAData(BaseResourceCheck):

    def __init__(self):
        """
        NIST.800-53.r5 CP-10, NIST.800-53.r5 CP-6(2), NIST.800-53.r5 SC-36, NIST.800-53.r5 SC-5(2),
        NIST.800-53.r5 SI-13(5)
        Elasticsearch domains should have at least three data nodes
        """
        name = "Ensure Elasticsearch domains have at least three data nodes"
        id = "CKV_AWS_319"
        supported_resources = ['aws_elasticsearch_domain', 'aws_opensearch_domain']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if conf.get("cluster_config") and isinstance(conf.get("cluster_config"), list):
            config = conf.get("cluster_config")[0]
            if isinstance(config, dict):
                if config.get('instance_count') and isinstance(config.get('instance_count'), list):
                    count = config.get('instance_count')[0]
                    if isinstance(count, int) and count >= 3:
                        return CheckResult.PASSED
        return CheckResult.FAILED


check = ElasticsearchDomainHAData()
