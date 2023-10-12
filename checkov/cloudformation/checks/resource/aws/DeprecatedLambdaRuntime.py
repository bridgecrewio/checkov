from typing import List, Any

from checkov.cloudformation.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck
from checkov.common.models.enums import CheckCategories


class DeprecatedLambdaRuntime(BaseResourceNegativeValueCheck):
    def __init__(self):
        name = "Ensure Lambda Runtime is not deprecated"
        id = "CKV_AWS_363"
        supported_resources = ['AWS::Lambda::Function', 'AWS::Serverless::Function']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "Properties/Runtime"

    def get_forbidden_values(self) -> List[Any]:
        return ["dotnetcore3.1", "nodejs12.x", "python3.6", "python2.7", "dotnet5.0", "dotnetcore2.1", "ruby2.5",
                "nodejs10.x", "nodejs8.10", "nodejs4.3", "nodejs6.10", "dotnetcore1.0", "dotnetcore2.0",
                "nodejs4.3-edge", "nodejs",
                # "python3.7", # Uncomment on Nov 27, 2023
                # "nodejs14.x", # Uncomment on Nov 27, 2023
                # "ruby2.7", # Uncomment on Dec 7, 2023
                # "provided", # Uncomment on Dec 31, 2023
                # "go1.x", # Uncomment on Dec 31, 2023
                # "java8", # Uncomment on Dec 31, 2023
                # "nodejs16.x", # Uncomment on Mar 11, 2024
                # "dotnet7", # Uncomment on May 14, 2024
                ]


check = DeprecatedLambdaRuntime()
