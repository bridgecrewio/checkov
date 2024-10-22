import pytest

from checkov.azure_pipelines.runner import Runner

@pytest.mark.parametrize(
    "key,file_path,expected_key, start_line, end_line",
    [
        ('jobs.jobs.CKV_AZUREPIPELINES_1[32:39]', '/checkov/tests/azure_pipelines/resources/azure-pipelines.yml',
         'jobs[0](FailTag)', 32, 39),
        ('stages[].jobs[].stages[].jobs[].CKV_AZUREPIPELINES_1[14:22]', '/checkov/tests/azure_pipelines/resources/azure-pipelines.yml',
         'stages[0](Example).jobs[0](FailNoTagDisplayName)', 14, 22),
        ('stages[].jobs[].stages[].jobs[].CKV_AZUREPIPELINES_1[22:29]', '/checkov/tests/azure_pipelines/resources/azure-pipelines.yml',
         'stages[0](Example).jobs[1](PassDigest)', 22, 29)
    ],
)
def test_get_resource(key, file_path, expected_key, definitions, supported_entities, start_line, end_line):
    runner = Runner()
    runner.definitions = definitions
    new_key = runner.get_resource(file_path, key, [], start_line, end_line)

    assert new_key == expected_key