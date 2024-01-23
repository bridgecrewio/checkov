

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck


class DeprecatedLambdaRuntime(BaseResourceNegativeValueCheck):
    def __init__(self):
        name = "Ensure Lambda Runtime is not deprecated"
        id = "CKV_AWS_363"
        supported_resources = ['aws_lambda_function']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "runtime"

    def get_forbidden_values(self):
        return ["dotnetcore3.1", "dotnet5.0", "dotnetcore2.1", "dotnetcore1.0", "dotnetcore2.0",
                "python3.6", "python2.7", "python3.7",
                "ruby2.5", "ruby2.7",
                "nodejs12.x", "nodejs10.x", "nodejs8.10", "nodejs4.3", "nodejs6.10",
                "nodejs4.3-edge", "nodejs", "nodejs14.x",
                "go1.x",
                # "python3.7" oct 14 2024
                # "provided", # Uncomment on Dec 31, 2023
                # "java8", # Uncomment on Dec 31, 2023
                # "nodejs16.x", # Uncomment on Jun 12, 2024
                # "dotnet7", # Uncomment on May 14, 2024
                ]


check = DeprecatedLambdaRuntime()
