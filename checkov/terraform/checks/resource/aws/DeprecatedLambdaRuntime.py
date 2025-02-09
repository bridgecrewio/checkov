from typing import List, Any

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck


class DeprecatedLambdaRuntime(BaseResourceNegativeValueCheck):
    def __init__(self) -> None:
        name = "Ensure Lambda Runtime is not deprecated"
        id = "CKV_AWS_363"
        supported_resources = ['aws_lambda_function']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "runtime"

    def get_forbidden_values(self) -> List[Any]:
        # Source: https://docs.aws.amazon.com/lambda/latest/dg/lambda-runtimes.html
        return ["python3.8", "python3.7", "python3.6", "python2.7",
                "dotnetcore3.1", "dotnet7", "dotnet6", "dotnet5.0", "dotnetcore2.1", "dotnetcore1.0", "dotnetcore2.0",
                "nodejs16.x", "nodejs14.x", "nodejs12.x", "nodejs10.x", "nodejs8.10", "nodejs6.10", "nodejs4.3", "nodejs4.3-edge", "nodejs",
                "java8", "go1.x", "provided", "ruby2.7", "ruby2.5"
                ]


check = DeprecatedLambdaRuntime()
