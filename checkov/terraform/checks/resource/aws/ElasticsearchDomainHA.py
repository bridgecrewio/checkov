from __future__ import annotations

from typing import Any

from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckCategories, CheckResult


class ElasticsearchDomainHA(BaseResourceCheck):
    def __init__(self) -> None:
        """NIST.800-53.r5 CP-10, NIST.800-53.r5 CP-6(2), NIST.800-53.r5 SC-36, NIST.800-53.r5 SC-5(2),
         NIST.800-53.r5 SI-13(5)
        Elasticsearch domains should be configured with at least three dedicated master nodes"""
        name = "Ensure Elasticsearch domains are configured with at least three dedicated master nodes for HA"
        id = "CKV_AWS_318"
        supported_resources = ("aws_elasticsearch_domain", "aws_opensearch_domain")
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        self.evaluated_keys = ["cluster_config"]
        config = conf.get("cluster_config")
        if config and isinstance(config, list):
            master_count = config[0].get("dedicated_master_count")
            if (
                master_count
                and isinstance(master_count, list)
                and isinstance(master_count[0], int)
                and master_count[0] >= 3
            ):
                zone_awareness = config[0].get("zone_awareness_enabled")
                if zone_awareness and isinstance(zone_awareness, list) and zone_awareness[0]:
                    return CheckResult.PASSED

        return CheckResult.FAILED


check = ElasticsearchDomainHA()
