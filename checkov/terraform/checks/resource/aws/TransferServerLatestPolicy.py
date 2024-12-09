from datetime import datetime

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class TransferServerLatestPolicy(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure AWS Transfer Server uses latest Security Policy"
        id = "CKV_AWS_380"
        supported_resources = ('aws_transfer_server',)
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def __check_policy_date(self, policy_string: str) -> bool:
        # Extract the year and month from the policy string
        # We assume that the year and month appear in the format 'YYYY-MM'

        # Split the string based on the '-' separator
        parts = policy_string.split('-')

        # Loop through the parts and check for the first valid year-month pair
        for i in range(len(parts) - 1):
            # Try to form a year-month date from consecutive parts
            year = parts[i]
            month = parts[i + 1]

            try:
                # If both year and month are integers and valid, create the date
                policy_date = datetime(int(year), int(month), 1)
                break
            except ValueError:
                continue
        else:
            # If no valid year-month combination is found, raise an error
            raise ValueError("No valid date found in the policy string.")

        # Get the current date
        current_date = datetime.now()

        # Calculate the time difference in months
        years_diff = current_date.year - policy_date.year
        months_diff = current_date.month - policy_date.month

        total_months_diff = years_diff * 12 + months_diff

        # If the difference is more than or equal to 24 months, return False
        return total_months_diff < 24

    def scan_resource_conf(self, conf: any) -> CheckResult:
        """
        Makes sure the Security Policy is no older than 2 years
        """
        security_policy = conf.get('security_policy_name')
        if security_policy:
            if self.__check_policy_date(security_policy[0]):
                return CheckResult.PASSED
        return CheckResult.FAILED  # default is TransferSecurityPolicy-2018-11 which is old: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/transfer_server

    def get_evaluated_key(self) -> str:
        return "security_policy_name"


check = TransferServerLatestPolicy()
