from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories, CheckResult
from typing import Any


class ACMCertSetLoggingPreference(BaseResourceValueCheck):

    def __init__(self):
        """
        To guard against SSL/TLS certificates that are issued by mistake or by a compromised CA,
        some browsers require that public certificates issued for your domain be recorded in a certificate
        transparency log.
         The domain name is recorded. The private key is not.
         Certificates that are not logged typically generate an error in the browser
        """
        name = "Verify logging preference for ACM certificates"
        id = "CKV_AWS_234"
        supported_resources = ['aws_acm_certificate']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.PASSED)

    def get_inspected_key(self):
        return "options/[0]/certificate_transparency_logging_preference"

    def get_expected_value(self) -> Any:
        return "ENABLED"


check = ACMCertSetLoggingPreference()
