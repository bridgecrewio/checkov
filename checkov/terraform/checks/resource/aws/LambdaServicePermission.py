from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class LambdaServicePermission(BaseResourceCheck):
    def __init__(self):
        # This is the full description of your check
        description = "Ensure that when a Lambda Function Permission is delegated to a service as principal, that the permission is scoped to either a SourceArn or a SourceAccount."

        # This is the Unique ID for your check
        id = "CKV_AWS_287"

        # These are the terraform objects supported by this check (ex: aws_iam_policy_document)
        supported_resources = ['aws_lambda_permission']

        # Valid CheckCategories are defined in checkov/common/models/enums.py
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=description, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        # Replace this with the custom logic for your check
        principal = conf.get("principal", [])
        self.evaluated_keys = ["principal"]
        principal_parts = principal[0].split('.')
        try:
            if principal_parts[1] == 'amazonaws' and principal_parts[2] == 'com':  # This confirms that the principal is set as a service principal.
                if 'source_arn' in conf.keys() or 'source_account' in conf.keys():  # If either of these are set, we're good and the check should pass.
                    self.evaluated_keys = ["principal", "source_account", "source_arn"]
                    return CheckResult.PASSED
                else:
                    self.evaluated_keys = ["principal", "source_account", "source_arn"]
                    return CheckResult.FAILED
        except IndexError:
            return CheckResult.PASSED
        return CheckResult.PASSED


check = LambdaServicePermission()
