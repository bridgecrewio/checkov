import pytest

from checkov.common.graph.graph_builder.utils import update_dictionary_attribute, join_double_quote_surrounded_dot_split

@pytest.mark.parametrize(
    "input_parts,expected_parts",
    [
        (
            ["google_project_iam_binding", 'role["roles/logging', 'admin"]'],
            ["google_project_iam_binding", 'role["roles/logging.admin"]'],
        ),
        (
            ["module", "google_project_iam_binding", 'role["roles/logging', 'admin"]'],
            ["module", "google_project_iam_binding", 'role["roles/logging.admin"]'],
        ),
        (
            [
                "module",
                "google_project_iam_binding",
                'role["roles/logging',
                'admin"]',
                "module",
                "google_project_iam_binding",
                'role["roles/logging',
                'admin"]',
            ],
            [
                "module",
                "google_project_iam_binding",
                'role["roles/logging.admin"]',
                "module",
                "google_project_iam_binding",
                'role["roles/logging.admin"]',
            ],
        ),
    ],
    ids=["resource", "module_resource", "complex"],
)
def test_join_double_quote_surrounded_dot_split(input_parts, expected_parts):
    assert join_double_quote_surrounded_dot_split(str_parts=input_parts) == expected_parts

def test_update_dictionary_attribute_nested():
    origin_config = {'aws_s3_bucket': {
        'destination': {'bucket': ['tf-test-bucket-destination-12345'], 'acl': ['${var.acl}'],
                        'versioning': [{'enabled': ['${var.is_enabled}']}]}}}
    key_to_update = 'versioning.enabled'
    new_value = [False]
    expected_config = {'aws_s3_bucket': {
        'destination': {'bucket': ['tf-test-bucket-destination-12345'], 'acl': ['${var.acl}'],
                        'versioning': [{'enabled': [False]}]}}}
    actual_config = update_dictionary_attribute(origin_config, key_to_update, new_value)
    assert expected_config == actual_config, f'failed to update config. expected: {expected_config}, got: {actual_config}'


def test_update_dictionary_attribute():
    origin_config = {'aws_s3_bucket': {
        'destination': {'bucket': ['tf-test-bucket-destination-12345'], 'acl': ['${var.acl}'],
                        'versioning': [{'enabled': ['${var.is_enabled}']}]}}}
    key_to_update = 'acl'
    new_value = ['public-read']
    expected_config = {'aws_s3_bucket': {
        'destination': {'bucket': ['tf-test-bucket-destination-12345'], 'acl': ['public-read'],
                        'versioning': [{'enabled': ['${var.is_enabled}']}]}}}
    actual_config = update_dictionary_attribute(origin_config, key_to_update, new_value)
    assert expected_config == actual_config, f'failed to update config.\nexpected: {expected_config}\ngot: {actual_config}'


def test_update_dictionary_locals():
    origin_config = {'aws_s3_bucket': {
        'destination': {'bucket': ['tf-test-bucket-destination-12345'], 'acl': ['${var.acl}'],
                        'versioning': [{'enabled': ['${var.is_enabled}']}]}}}
    key_to_update = 'acl'
    new_value = ['public-read']
    expected_config = {'aws_s3_bucket': {
        'destination': {'bucket': ['tf-test-bucket-destination-12345'], 'acl': ['public-read'],
                        'versioning': [{'enabled': ['${var.is_enabled}']}]}}}
    actual_config = update_dictionary_attribute(origin_config, key_to_update, new_value)
    assert expected_config == actual_config, f'failed to update config.\nexpected: {expected_config}\ngot: {actual_config}'
