from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck


class RDSPubliclyAccessible(BaseResourceNegativeValueCheck):
    def __init__(self):
        name = "Ensure all data stored in RDS is not publicly accessible"
        id = "CKV_AWS_17"
        supported_resources = ['aws_db_instance', 'aws_rds_cluster_instance']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'publicly_accessible'

    def get_forbidden_values(self):
        return [True]


check = RDSPubliclyAccessible()
