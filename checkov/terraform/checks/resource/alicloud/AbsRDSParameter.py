from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class AbsRDSParameter(BaseResourceCheck):
    def __init__(self, check_id, parameter):
        name = "Ensure RDS instance has %s enabled" % parameter
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
        if conf.get("parameters") and isinstance(conf.get("parameters"), list):
            params = conf.get("parameters")
            for param in params:
                if param['name'][0] == self.parameter and param['value'][0] == 'ON':
                    return CheckResult.PASSED
        return CheckResult.FAILED
