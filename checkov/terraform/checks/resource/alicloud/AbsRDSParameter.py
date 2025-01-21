from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class AbsRDSParameter(BaseResourceCheck):
    def __init__(self, check_id, parameter):
        name = f"Ensure RDS instance has {parameter} enabled"
        supported_resources = ['alicloud_db_instance']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=check_id, categories=categories, supported_resources=supported_resources)
        self.parameter = parameter

    def scan_resource_conf(self, conf):
        """
            Looks at configuration of RDS logging parameters :

        :param conf: alicloud_db_instance configuration
        :return: <CheckResult>
        """
        params = conf.get("parameters")
        if params and isinstance(params, list):
            for param in params:
                if not isinstance(param, dict):
                    return CheckResult.UNKNOWN
                if param['name'][0] == self.parameter and (param['value'][0]).lower() == 'on':
                    return CheckResult.PASSED
        return CheckResult.FAILED

    def get_evaluated_keys(self):
        return ["parameters"]
