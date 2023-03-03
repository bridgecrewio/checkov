import pytest

from checkov.gitlab_ci.runner import Runner


@pytest.mark.parametrize(
    "key,file_path,expected_key, start_line, end_line",
    [
        ('*.script[].*.script[].CKV_GITLABCI_1[19:19]', '/checkov/tests/gitlab_ci/resources/images/.gitlab-ci.yml',
         'test.script', 19, 19),
        ('*.rules.*.rules.CKV_GITLABCI_2[7:9]', '/checkov/tests/gitlab_ci/resources/two/.gitlab-ci.yml',
         'planOnlySubset', 7, 9),
    ],
)
def test_get_resource(key, file_path, expected_key, definitions, start_line, end_line):
    runner = Runner()
    runner.definitions = definitions
    new_key = runner.get_resource(file_path, key, [], start_line, end_line)

    assert new_key == expected_key