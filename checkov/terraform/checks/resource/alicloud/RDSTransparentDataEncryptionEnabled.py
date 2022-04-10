from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from typing import Any

supported_mysql_engines = ["5.6", "5.7", "8", "8.0"]
supported_sql_engines = ["08r2_ent_ha", "2012_ent_ha", "2016_ent_ha", "2017_ent", "2019_std_ha", "2019_ent"]


class RDSTransparentDataEncryptionEnabled(BaseResourceValueCheck):
    def __init__(self):
        """
        Check valid db engines here: https://www.alibabacloud.com/help/en/apsaradb-for-rds/latest/create-an-instance
        """

        name = "Ensure Transparent Data Encryption is Enabled on instance"
        id = "CKV_ALI_22"
        supported_resources = ['alicloud_db_instance']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf) -> CheckResult:
        if conf.get("engine") == ["MySQL"] or conf.get("engine") == ["SQLServer"]:
            if conf.get("engine_version") and isinstance(conf.get("engine_version"), list):
                if conf.get("engine_version")[0] in supported_mysql_engines or \
                        conf.get("engine_version")[0] in supported_sql_engines:
                    if conf.get("tde_status") == ["Enabled"]:
                        return CheckResult.PASSED
                    self.evaluated_keys = ["engine_version"]
                    return CheckResult.FAILED
        return CheckResult.UNKNOWN

    def get_inspected_key(self):
        return "tde_status"

    def get_expected_value(self) -> Any:
        return "Enabled"


check = RDSTransparentDataEncryptionEnabled()
