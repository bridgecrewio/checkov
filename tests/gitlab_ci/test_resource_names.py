import pytest

from checkov.gitlab_ci.runner import Runner


@pytest.mark.parametrize(
    "key,file_path,expected_key",
    [
        ('*.script[].*.script[].CKV_GITLABCI_1[19:19]', '/checkov/tests/gitlab_ci/resources/images/.gitlab-ci.yml',
         'test.script'),
        ('*.rules.*.rules.CKV_GITLABCI_2[7:9]', '/checkov/tests/gitlab_ci/resources/two/.gitlab-ci.yml',
         'planOnlySubset'),
    ],
)
def test_get_resource(key, file_path, expected_key, definitions):
    runner = Runner()
    runner.definitions = definitions
    new_key = runner.get_resource(file_path, key, [], {})

    assert new_key == expected_key


@pytest.mark.parametrize(
    "key,expected_start_line,expected_end_line",
    [
        ("*.script[].*.script[].CKV_GITLABCI_1[19:19]", 19, 19),
        ("*.rules.*.rules.CKV_GITLABCI_2[7:9]", 7, 9),
        ("*.script[].CKV_GITLABCI_1", -1, -1)
    ]
)
def test_get_start_and_end_lines(key, expected_start_line, expected_end_line):
    runner = Runner()
    start_line, end_line = runner.get_start_and_end_lines(key)

    assert start_line == expected_start_line
    assert end_line == expected_end_line
