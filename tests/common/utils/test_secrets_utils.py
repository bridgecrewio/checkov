import os

from checkov.common.models.enums import CheckResult
from checkov.common.util.secrets import omit_secret_value_from_checks, omit_secret_value_from_graph_checks
from checkov.common.graph.checks_infra.base_check import BaseGraphCheck
from checkov.main import Checkov
from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.provider.aws.credentials import AWSCredentials
from checkov.terraform.checks.resource.azure.SecretExpirationDate import SecretExpirationDate


def test_omit_secret_value_from_checks_by_attribute(
        tfplan_resource_lines_with_secrets,
        tfplan_resource_config_with_secrets,
        tfplan_resource_lines_without_secrets
):
    check = SecretExpirationDate()
    check.entity_type = 'azurerm_key_vault_secret'
    check_result = {'result': CheckResult.FAILED}
    resource_attributes_to_omit = {'azurerm_key_vault_secret': {'value'}}

    assert omit_secret_value_from_checks(
        check,
        check_result,
        tfplan_resource_lines_with_secrets,
        tfplan_resource_config_with_secrets,
        resource_attributes_to_omit
    ) == tfplan_resource_lines_without_secrets


def test_omit_secret_value_from_checks_by_secret(
        aws_provider_lines_with_secrets,
        aws_provider_config_with_secrets,
        aws_provider_lines_without_secrets
):
    check = AWSCredentials()
    check_result = {'result': CheckResult.FAILED}

    assert omit_secret_value_from_checks(
        check,
        check_result,
        aws_provider_lines_with_secrets,
        aws_provider_config_with_secrets
    ) == aws_provider_lines_without_secrets


def test_omit_secret_value_from_checks_by_secret_2():
    entity_lines_with_secrets = [
        (93, '          "values": {\n'),
        (94, '            "content_type": null,\n'),
        (95, '            "expiration_date": null,\n'),
        (96, '            "key_vault_id": "/subscriptions/my-subscription/resourceGroups/my-rg/providers/Microsoft.KeyVault/vaults/my-vault",\n'),
        (97, '            "name": "my-key-vault",\n'),
        (98, '            "not_before_date": null,\n'),
        (99, '            "tags": null,\n'),
        (100, '            "timeouts": null,\n'),
        (101, '            "value": "-----BEGIN RSA PRIVATE KEY-----\\nMOCKKEYmer0YcjoLJVs4VvyLaigj7ygbpplVefQFHXseE7Lx0S2YBA6cg5SHoe4huMCsLwqyHJane2aseEq6oreSUG4Fzk3XpZSJ8fhNTdH2XHjCiK2LmAMHLV34adw2DEVKESa3PTf86EPIXu77qOH5HMl9tCXl9e1xf3wluaecOjdamK9HcNv8l0R58tTIuHpK+HiT69EHUjn7Igv904vPoTSl3f0Ut+xYTWOBBQJRG9YI7fHLJTL5ki1Hbb6Kl/6rsFur3P32kHQqFtDb9l7AQ/J68ws6MNfi+n5EylyRMgWkDRaryDPfRp9Aoe82Fo0pZDarEmphE58+FTKw5eC6qh3\\n-----END RSA PRIVATE KEY-----\\n"\n')
    ]
    entity_config_with_secrets = {
        'content_type': [None],
        'expiration_date': [None],
        'key_vault_id': ['/subscriptions/my-subscription/resourceGroups/my-rg/providers/Microsoft.KeyVault/vaults/my-vault'],
        'name': ['my-key-vault'], 'not_before_date': [None], 'tags': [None], 'timeouts': [None],
        'value': ['-----BEGIN RSA PRIVATE KEY-----\nMOCKKEYmer0YcjoLJVs4VvyLaigj7ygbpplVefQFHXseE7Lx0S2YBA6cg5SHoe4huMCsLwqyHJane2aseEq6oreSUG4Fzk3XpZSJ8fhNTdH2XHjCiK2LmAMHLV34adw2DEVKESa3PTf86EPIXu77qOH5HMl9tCXl9e1xf3wluaecOjdamK9HcNv8l0R58tTIuHpK+HiT69EHUjn7Igv904vPoTSl3f0Ut+xYTWOBBQJRG9YI7fHLJTL5ki1Hbb6Kl/6rsFur3P32kHQqFtDb9l7AQ/J68ws6MNfi+n5EylyRMgWkDRaryDPfRp9Aoe82Fo0pZDarEmphE58+FTKw5eC6qh3\n-----END RSA PRIVATE KEY-----\n'],
        '__startline__': [93], '__endline__': [102], 'start_line': [92], 'end_line': [101],
        'references_': ['tls_private_key.ssh.private_key_pem', 'tls_private_key.ssh'],
        '__address__': 'azurerm_key_vault_secret.akv_009_pass_01', '__change_actions__': ['create']}
    check = SecretExpirationDate()
    check.entity_type = 'azurerm_key_vault_secret'
    check_result = {'result': CheckResult.FAILED}

    entity_lines_without_secrets = [
        (93, '          "values": {\n'),
        (94, '            "content_type": null,\n'),
        (95, '            "expiration_date": null,\n'),
        (96, '            "key_vault_id": "/subscriptions/my-subscription/resourceGroups/my-rg/providers/Microsoft.KeyVault/vaults/my-vault",\n'),
        (97, '            "name": "my-key-vault",\n'),
        (98, '            "not_before_date": null,\n'),
        (99, '            "tags": null,\n'),
        (100, '            "timeouts": null,\n'),
        (101, '            "value": "-----**********--\\n"\n')
    ]
    resource_attributes_to_omit = {'azurerm_key_vault_secret': {'value'}}

    result = omit_secret_value_from_checks(
        check,
        check_result,
        entity_lines_with_secrets,
        entity_config_with_secrets,
        resource_attributes_to_omit
    )

    assert result == entity_lines_without_secrets


def test_omit_secret_value_from_graph_checks_by_attribute(
        tfplan_resource_lines_with_secrets,
        tfplan_resource_config_with_secrets,
        tfplan_resource_lines_without_secrets
):
    check = BaseGraphCheck()
    check.resource_types = ['azurerm_key_vault_secret']
    check_result = {'result': CheckResult.FAILED}
    resource_attributes_to_omit = {'azurerm_key_vault_secret': {'value'}}

    result = omit_secret_value_from_graph_checks(
        check,
        check_result,
        tfplan_resource_lines_with_secrets,
        tfplan_resource_config_with_secrets,
        resource_attributes_to_omit
    )

    assert result == tfplan_resource_lines_without_secrets


def test_omit_secret_value_from_graph_checks_by_attribute_skip_non_string():
    # given
    check = BaseGraphCheck()
    check.resource_types = ['aws_ssm_parameter']
    check_result = {'result': CheckResult.FAILED}
    entity_code_lines = [
        (22, 'resource "aws_ssm_parameter" "aws_ssm_parameter_foo" {\n'),
        (23, '  name        = "foo"\n'),
        (24, '  description = "Parameter foo"\n'),
        (25, '  type        = "String"\n'),
        (26, '  tier        = "Advanced"\n'),
        (27, "  value = jsonencode({\n"),
        (28, '    "foo" : {\n'),
        (29, '      "hello" : "world",\n'),
        (30, '      "answer " : 42\n'),
        (31, "     }\n"),
        (32, "  })\n"),
        (33, "}\n"),
    ]
    entity_config = {
        "__address__": "aws_ssm_parameter.aws_ssm_parameter_foo",
        "__end_line__": 33,
        "__start_line__": 22,
        "description": ["Parameter foo"],
        "name": ["foo"],
        "tier": ["Advanced"],
        "type": ["String"],
        "value": [
            {
                "foo": {
                    "answer ": 42,
                    "hello": "world",
                }
            }
        ],
    }
    resource_attributes_to_omit = {'aws_ssm_parameter': {'value'}}

    # when
    result = omit_secret_value_from_graph_checks(
        check=check,
        check_result=check_result,
        entity_code_lines=entity_code_lines,
        entity_config=entity_config,
        resource_attributes_to_omit=resource_attributes_to_omit
    )

    # then
    assert result == [
        (22, 'resource "aws_ssm_parameter" "aws_ssm_parameter_foo" {\n'),
        (23, '  name        = "foo"\n'),
        (24, '  description = "Parameter foo"\n'),
        (25, '  type        = "String"\n'),
        (26, '  tier        = "Advanced"\n'),
        (27, "  value = jsonencode({\n"),
        (28, '    "foo" : {\n'),
        (29, '      "hello" : "world",\n'),
        (30, '      "answer " : 42\n'),
        (31, "     }\n"),
        (32, "  })\n"),
        (33, "}\n"),
    ]


def test_omit_secret_value_from_checks_by_attribute_runner_filter_resource_config(
        tfplan_resource_lines_with_secrets,
        tfplan_resource_config_with_secrets,
        tfplan_resource_lines_without_secrets
):
    argv = [
        "--config-file",
        f"{os.path.dirname(os.path.realpath(__file__))}/../resource_attr_to_omit_configs/real_keys.yml"
    ]
    ckv = Checkov(argv=argv)
    runner_filter = RunnerFilter(resource_attr_to_omit=ckv.config.mask)
    check = SecretExpirationDate()
    check.entity_type = 'azurerm_key_vault_secret'
    check_result = {'result': CheckResult.FAILED}

    assert omit_secret_value_from_checks(
        check,
        check_result,
        tfplan_resource_lines_with_secrets,
        tfplan_resource_config_with_secrets,
        runner_filter.resource_attr_to_omit) == tfplan_resource_lines_without_secrets


# ToDo: Uncomment if we want to support universal masking
# def test_omit_secret_value_from_checks_by_attribute_runner_filter_universal_config(
#         tfplan_resource_lines_with_secrets,
#         tfplan_resource_config_with_secrets,
#         tfplan_resource_lines_without_secrets
# ):
#     argv = [
#         "--config-file",
#         f"{os.path.dirname(os.path.realpath(__file__))}/../resource_attr_to_omit_configs/universal_key.yml"
#     ]
#     ckv = Checkov(argv=argv)
#     runner_filter = RunnerFilter(resource_attr_to_omit=ckv.config.mask)
#     check = SecretExpirationDate()
#     check.entity_type = 'azurerm_key_vault_secret'
#     check_result = {'result': CheckResult.FAILED}
#
#     assert omit_secret_value_from_checks(
#         check,
#         check_result,
#         tfplan_resource_lines_with_secrets,
#         tfplan_resource_config_with_secrets,
#         runner_filter.resource_attr_to_omit) == tfplan_resource_lines_without_secrets

def test_omit_secret_value_from_checks_by_attribute_runner_filter_duplicated_config(
        tfplan_resource_lines_with_secrets,
        tfplan_resource_config_with_secrets,
        tfplan_resource_lines_without_secrets
):
    argv = [
        "--config-file",
        f"{os.path.dirname(os.path.realpath(__file__))}/../resource_attr_to_omit_configs/duplicated_key.yml"
    ]
    ckv = Checkov(argv=argv)
    runner_filter = RunnerFilter(resource_attr_to_omit=ckv.config.mask)
    check = SecretExpirationDate()
    check.entity_type = 'azurerm_key_vault_secret'
    check_result = {'result': CheckResult.FAILED}
    assert omit_secret_value_from_checks(
        check,
        check_result,
        tfplan_resource_lines_with_secrets,
        tfplan_resource_config_with_secrets,
        runner_filter.resource_attr_to_omit) == tfplan_resource_lines_without_secrets


# ToDo: Uncomment if we want to support universal masking
# def test_omit_secret_value_from_checks_by_attribute_runner_filter_multiple_keys(
#         tfplan_resource_lines_with_secrets,
#         tfplan_resource_config_with_secrets,
#         tfplan_resource_lines_without_secrets_multiple_keys
# ):
#
#     argv = [
#         "--config-file",
#         f"{os.path.dirname(os.path.realpath(__file__))}/../resource_attr_to_omit_configs/multiple_keys.yml"
#     ]
#     ckv = Checkov(argv=argv)
#     runner_filter = RunnerFilter(resource_attr_to_omit=ckv.config.mask)
#
#     check = SecretExpirationDate()
#     check.entity_type = 'azurerm_key_vault_secret'
#     check_result = {'result': CheckResult.FAILED}
#
#     assert omit_secret_value_from_checks(
#         check,
#         check_result,
#         tfplan_resource_lines_with_secrets,
#         tfplan_resource_config_with_secrets,
#         runner_filter.resource_attr_to_omit
#     ) == tfplan_resource_lines_without_secrets_multiple_keys
