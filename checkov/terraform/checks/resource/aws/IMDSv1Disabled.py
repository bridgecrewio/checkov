from checkov.common.models.enums import (
    CheckCategories,
    CheckResult,
)
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class IMDSv1Disabled(BaseResourceCheck):

    def __init__(self):
        name = "Ensure Instance Metadata Service Version 1 is not enabled"
        id = "CKV_AWS_79"
        categories = [CheckCategories.GENERAL_SECURITY]
        supported_resources = ['aws_instance', 'aws_launch_template']
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_resources=supported_resources,
        )

    def scan_resource_conf(self, conf):
        """
        Looks for if the metadata service is disabled or requires session tokens:
            https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/instance#metadata-options
            or
            https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/launch_template#metadata-options

        :param conf: dict of supported resource configuration
        :return: <CheckResult>
        """
        if (
            'metadata_options' not in conf.keys()
            or
            not isinstance(conf['metadata_options'][0], dict)
        ):
            return CheckResult.FAILED

        metadata_options = conf['metadata_options'][0]
        if (
            metadata_options.get("http_tokens") == ["required"]
            or
            metadata_options.get("http_endpoint") == ["disabled"]
        ):
            return CheckResult.PASSED
        return CheckResult.FAILED


check = IMDSv1Disabled()
