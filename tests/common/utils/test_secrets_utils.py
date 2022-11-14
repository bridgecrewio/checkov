from checkov.common.util.secrets import omit_secret_value_from_checks
from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.azure.SecretExpirationDate import SecretExpirationDate
from checkov.terraform.checks.provider.aws.credentials import AWSCredentials


def test_omit_secret_value_from_checks_by_attribute(tfplan_resource_lines_with_secrets, tfplan_resource_config_with_secrets,
                                    tfplan_resource_lines_without_secrets):
    check = SecretExpirationDate()
    check.entity_type = 'azurerm_key_vault_secret'
    check_result = {'result': CheckResult.FAILED}
    resource_attributes_to_omit = {'azurerm_key_vault_secret': 'value'}

    assert omit_secret_value_from_checks(check, check_result, tfplan_resource_lines_with_secrets,
                                         tfplan_resource_config_with_secrets, resource_attributes_to_omit
                                         ) == tfplan_resource_lines_without_secrets


def test_omit_secret_value_from_checks_by_secret(aws_provider_lines_with_secrets, aws_provider_config_with_secrets,
                                    aws_provider_lines_without_secrets):
    check = AWSCredentials()
    check_result = {'result': CheckResult.FAILED}

    assert omit_secret_value_from_checks(check, check_result, aws_provider_lines_with_secrets,
                                         aws_provider_config_with_secrets
                                         ) == aws_provider_lines_without_secrets
