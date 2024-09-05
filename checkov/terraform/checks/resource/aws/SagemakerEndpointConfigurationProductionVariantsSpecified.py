from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck

class SagemakerEndpointConfigurationProductionVariantsSpecified(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Amazon SageMaker endpoint configuration has at least one production variant specified"
        id = "CKV_AWS_991" 
        supported_resources = ['aws_sagemaker_endpoint_configuration']
        categories = [CheckCategories.AI_AND_ML]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        production_variants = conf.get("production_variants")
        if production_variants:
            if isinstance(production_variants, list):
                return CheckResult.PASSED if production_variants else CheckResult.FAILED
            elif isinstance(production_variants, dict):
                return CheckResult.PASSED if 'variant_name' in production_variants and production_variants['variant_name'] else CheckResult.FAILED
        return CheckResult.FAILED

check = SagemakerEndpointConfigurationProductionVariantsSpecified()
