from checkov.common.models.consts import ANY_VALUE
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class GoogleIAMWorkloadIdentityConditional(BaseResourceValueCheck):
    def __init__(self):
        """
        A configuration for an external workload identity pool provider should have conditions set.
        In GitHub Actions, one can authenticate to Google Cloud by setting values for workload_identity_provider and service_account and requesting a short-lived OIDC token which is then used to execute commands as that Service Account. If you don't specify a condition in the workload identity provider pool configuration, then any GitHub Action can assume this role and act as that Service Account.
        This can be checked in Terraform configs by looking at whether a google_iam_workload_identity_pool_provider has the attribute_condition field set.

        Link: https://www.revblock.dev/exploiting-misconfigured-google-cloud-service-accounts-from-github-actions/
        """

        name = "Ensure IAM workload identity pool provider is restricted"
        id = "CKV_GCP_118"
        supported_resources = ['google_iam_workload_identity_pool_provider']
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'attribute_condition'

    def get_expected_value(self):
        return ANY_VALUE


check = GoogleIAMWorkloadIdentityConditional()
