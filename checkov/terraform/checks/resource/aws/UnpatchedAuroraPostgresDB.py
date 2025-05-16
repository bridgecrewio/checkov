from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class UnpatchedAuroraPostgresDB(BaseResourceCheck):

    def __init__(self):
        name = "Ensure AWS Aurora PostgreSQL is not exposed to local file read vulnerability"
        id = "CKV_AWS_388"
        supported_resources = ['aws_db_instance']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'engine' in conf and 'aurora-postgresql' in conf['engine']:
            if 'engine_version' in conf and conf['engine_version'][0] in ['10.11', '10.12', '10.13', '11.6', '11.7', '11.8']:
                self.evaluated_keys = ['engine', 'engine-version']
                return CheckResult.FAILED
        return CheckResult.PASSED


check = UnpatchedAuroraPostgresDB()
