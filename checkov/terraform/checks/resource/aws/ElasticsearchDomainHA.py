from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.common.util.type_forcers import force_int


class ElasticsearchDomainHA(BaseResourceCheck):

    def __init__(self):
        """NIST.800-53.r5 CP-10, NIST.800-53.r5 CP-6(2), NIST.800-53.r5 SC-36, NIST.800-53.r5 SC-5(2),
         NIST.800-53.r5 SI-13(5)
        ElasticSearch and OpenSearch domains should have at least three data nodes"""
        name = "Ensure ElasticSearch and OpenSearch domains should have at least three data nodes for HA"
        id = "CKV_AWS_317"
        supported_resources = ['aws_elasticsearch_domain', 'aws_opensearch_domain']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if conf.get("cluster_config") and isinstance(conf.get("cluster_config"), list):
            config = conf.get("cluster_config")[0]
            if config.get("dedicated_master_count") and isinstance(config.get("dedicated_master_count"), list) and \
                    len(config.get("dedicated_master_count")) > 0:
                if force_int(config.get("dedicated_master_count")[0]) >= 3:
                    if config.get("zone_awareness_enabled") and isinstance(config.get("zone_awareness_enabled"), list):
                        zone = config.get("zone_awareness_enabled")[0]
                        if zone:
                            return CheckResult.PASSED

        self.evaluated_keys = ["cluster_config"]
        return CheckResult.FAILED


check = ElasticsearchDomainHA()
