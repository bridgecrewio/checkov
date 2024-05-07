from typing import List, Any

from checkov.cloudformation.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck
from checkov.common.models.enums import CheckCategories


class DeprecatedLambdaRuntime(BaseResourceNegativeValueCheck):
    def __init__(self) -> None:
        name = "Ensure Lambda Runtime is not deprecated"
        id = "CKV_AWS_363"
        supported_resources = ['AWS::Lambda::Function', 'AWS::Serverless::Function']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "Properties/Runtime"

    def get_forbidden_values(self) -> List[Any]:
        # Source: https://docs.aws.amazon.com/lambda/latest/dg/lambda-runtimes.html
        return ["dotnetcore3.1", "nodejs12.x", "python3.6", "python2.7", "dotnet5.0", "dotnetcore2.1", "ruby2.5",
                "nodejs10.x", "nodejs8.10", "nodejs4.3", "nodejs6.10", "dotnetcore1.0", "dotnetcore2.0",
                "nodejs4.3-edge", "nodejs", "java8", "python3.7", "go1.x", "provided", "ruby2.7", "nodejs14.x"
                # "nodejs16.x", # Uncomment on Jun 12, 2024
                # "python3.8". # Uncomment on Oct 14, 2024
                # "dotnet7", # Uncomment on May 14, 2024
                # "dotnet6", # Uncomment on Nov 12, 2024
                ]


check = DeprecatedLambdaRuntime()
