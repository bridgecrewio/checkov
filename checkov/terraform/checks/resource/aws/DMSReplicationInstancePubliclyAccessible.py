from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck


class DMSReplicationInstancePubliclyAccessible(BaseResourceNegativeValueCheck):
    def __init__(self):
        name = "DMS replication instance should not be publicly accessible"
        id = "CKV_AWS_89"
        supported_resources = ['aws_dms_replication_instance']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'publicly_accessible'

    def get_forbidden_values(self):
        return [True]


check = DMSReplicationInstancePubliclyAccessible()
