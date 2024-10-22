from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class NeptuneDBClustersCopyTagsToSnapshots(BaseResourceValueCheck):
    def __init__(self):
        description = "Neptune DB clusters should be configured to copy tags to snapshots"
        id = "CKV_AWS_362"
        supported_resources = ['aws_neptune_cluster']
        categories = [CheckCategories.BACKUP_AND_RECOVERY]
        super().__init__(name=description, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "copy_tags_to_snapshot"


check = NeptuneDBClustersCopyTagsToSnapshots()
