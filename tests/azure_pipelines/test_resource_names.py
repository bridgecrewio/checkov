import pytest

from checkov.azure_pipelines.runner import Runner

@pytest.mark.parametrize(
    "key,file_path,expected_key",
    [
        ('jobs.jobs.CKV_AZUREPIPELINES_1[32:39]', '/checkov/tests/azure_pipelines/resources/azure-pipelines.yml',
         'jobs[0](FailTag)'),
        ('stages[].jobs[].stages[].jobs[].CKV_AZUREPIPELINES_1[14:22]', '/checkov/tests/azure_pipelines/resources/azure-pipelines.yml',
         'stages[0](Example).jobs[0](FailNoTagDisplayName)'),
        ('stages[].jobs[].stages[].jobs[].CKV_AZUREPIPELINES_1[22:29]', '/checkov/tests/azure_pipelines/resources/azure-pipelines.yml',
         'stages[0](Example).jobs[1](PassDigest)')
    ],
)
def test_get_resource(key, file_path, expected_key, definitions, supported_entities):
    runner = Runner()
    runner.definitions = definitions
    new_key = runner.get_resource(file_path, key, [], definitions)

    assert new_key == expected_key


@pytest.mark.parametrize(
    "key,expected_start_line,expected_end_line",
    [
        ("jobs.jobs.CKV_AZUREPIPELINES_1[32:39]", 32, 39),
        ("stages[].jobs[].stages[].jobs[].CKV_AZUREPIPELINES_1[14:22]", 14, 22),
        ("stages[].jobs[].stages[].jobs[].CKV_AZUREPIPELINES_1", -1, -1)
    ]
)
def test_get_start_and_end_lines(key, expected_start_line, expected_end_line):
    runner = Runner()
    start_line, end_line = runner.get_start_and_end_lines(key)

    assert start_line == expected_start_line
    assert end_line == expected_end_line
