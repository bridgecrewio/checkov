from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck


class CodebuildS3LogsEncrypted(BaseResourceNegativeValueCheck):
    def __init__(self):
        """
        NIST.800-53.r5 CA-9(1), NIST.800-53.r5 CM-3(6), NIST.800-53.r5 SC-13, NIST.800-53.r5 SC-28,
        NIST.800-53.r5 SC-28(1), NIST.800-53.r5 SI-7(6)
        """
        name = "Ensure that CodeBuild S3 logs are encrypted"
        id = "CKV_AWS_311"
        supported_resource = ['aws_codebuild_project']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resource)

    def get_inspected_key(self):
        return "logs_config/[0]/s3_logs/[0]/encryption_disabled"

    def get_forbidden_values(self):
        return [True]


check = CodebuildS3LogsEncrypted()
