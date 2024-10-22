from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories, CheckResult


class RDSInstancePerformanceInsights(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that RDS instances have performance insights enabled"
        id = "CKV_AWS_353"
        supported_resources = ('aws_rds_cluster_instance', 'aws_db_instance')
        categories = (CheckCategories.LOGGING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        # Performance Insights is not available  for MariaDB and MySQL using certain classes: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_PerfInsights.Overview.Engines.html
        if conf.get("engine") in (["mariadb"], ["mysql"], ["aws_rds_cluster.default.engine"]):
            if conf.get("instance_class") in (["db.t2.micro"], ["db.t2.small"], ["db.t3.micro"], ["db.t3.small"],
                                              ["db.t4g.micro"], ["db.t4g.small"]):
                return CheckResult.UNKNOWN
        # Performance Insights is not supported for DB2: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.RDS_Fea_Regions_DB-eng.Feature.PerformanceInsights.html
        if conf.get("engine") in (["db2-se"], ["db2-ae"]):
            return CheckResult.UNKNOWN
        return super().scan_resource_conf(conf)

    def get_inspected_key(self) -> str:
        return 'performance_insights_enabled'


check = RDSInstancePerformanceInsights()
