from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class RDSClusterCopyTags(BaseResourceValueCheck):
    def __init__(self) -> None:
        """
        NIST.800-53.r5 CA-9(1), NIST.800-53.r5 CM-2, NIST.800-53.r5 CM-2(2)
        RDS DB clusters should be configured to copy tags to snapshots
        """
        name = "Ensure RDS cluster configured to copy tags to snapshots"
        id = "CKV_AWS_313"
        supported_resources = ("aws_rds_cluster",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "copy_tags_to_snapshot"


check = RDSClusterCopyTags()
