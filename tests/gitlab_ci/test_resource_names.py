import pytest

from checkov.gitlab_ci.runner import Runner


@pytest.mark.parametrize(
    "key,file_path,expected_key",
    [
        ('*.script[].*.script[].CKV_GITLABCI_1', 'checkov/tests/gitlab_ci/resources/images/.gitlab-ci.yml',
         '.gitlab-ci.yml/*.script[].*.script[]'),
        ('*.rules.*.rules.CKV_GITLABCI_2[4:9]', 'checkov/tests/gitlab_ci/resources/two/.gitlab-ci.yaml',
         '.gitlab-ci.yaml/*.rules.*.rules'),
    ],
)
def test_get_resource(key, file_path, expected_key):
    runner = Runner()

    new_key = runner.get_resource(file_path, key, [], {})

    assert new_key == expected_key
