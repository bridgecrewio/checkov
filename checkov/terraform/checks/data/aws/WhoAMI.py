from typing import Dict, Any, List

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.data.base_check import BaseDataCheck


class WhoAMI(BaseDataCheck):
    def __init__(self) -> None:
        name = "Reduce potential for WhoAMI cloud image name confusion attack"
        id = "CKV_AWS_386"
        supported_data = ['aws_ami']
        categories = [CheckCategories.SUPPLY_CHAIN]
        super().__init__(name=name, id=id, categories=categories, supported_data=supported_data)

    def scan_data_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        """
        Validates AWS AMI configuration to prevent WhoAMI vulnerability
        by checking for unspecified owners and overly permissive name patterns

        :param conf: aws_ami data source configuration
        :return: <CheckResult>
        """
        # Check if owners is specified and not empty
        owners = conf.get("owners", [])
        if not owners:
            filters = conf.get("filter", [])
            if not isinstance(filters, list):
                filters = [filters]

            for filter_block in filters:
                if isinstance(filter_block, dict):
                    # Check name filter specifically
                    if filter_block.get("name", [""])[0] == "name":
                        values = filter_block.get("values")[0]
                        for value in values:
                            # Check for overly permissive patterns
                            if '*' in value or '?' in value:
                                return CheckResult.FAILED

        return CheckResult.PASSED


check = WhoAMI()
