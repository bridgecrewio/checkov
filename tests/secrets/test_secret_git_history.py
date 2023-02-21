from typing import Dict
from unittest import mock

from detect_secrets import SecretsCollection

from checkov.secrets.scan_git_history import scan_history
from checkov.secrets.runner import Runner
from checkov.runner_filter import RunnerFilter
from detect_secrets.settings import transient_settings


def mock_git_repo_commits(root_folder: str) -> Dict[str, Dict[str, str]]:
    return {
        "8a21fa691e17907afee57e93b7820c5943b12746":
            {
                "Dockerfile": "diff --git a/Dockerfile b/Dockerfile\nindex 0000..0000 0000\n--- a/Dockerfile\n+++ b/Dockerfile\n@@ -4,6 +4,8 @@ FROM public.ecr.aws/lambda/python:3.9\n \n ENV PIP_ENV_VERSION=\"2022.1.8\"\n \n+ENV AWS_ACCESS_KEY_ID=\"wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY\"\n+\n COPY Pipfile Pipfile.lock ./\n \n RUN pip install pipenv==${PIP_ENV_VERSION} \\\n"
            },
        "d3249f33376b94a939b67a638aba4557b071875f":
            {
                "Dockerfile": "diff --git a/Dockerfile b/Dockerfile\nindex 0000..0000 0000\n--- a/Dockerfile\n+++ b/Dockerfile\n@@ -1,10 +1,9 @@\n #checkov:skip=CKV_DOCKER_2:Healthcheck is not relevant for ephemral containers\n #checkov:skip=CKV_DOCKER_3:User is created automatically by lambda runtime\n FROM public.ecr.aws/lambda/python:3.9\n-\n+ENV AWS_ACCESS_KEY_ID=\"wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY\"\n ENV PIP_ENV_VERSION=\"2022.1.8\"\n \n-ENV AWS_ACCESS_KEY_ID=\"wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY\"\n \n COPY Pipfile Pipfile.lock ./\n \n"
            },
        "3d79bba03c6f0ddcfb8334f531701942c4be0f32":
            {
                "Dockerfile": "diff --git a/Dockerfile b/Dockerfile\nindex 0000..0000 0000\n--- a/Dockerfile\n+++ b/Dockerfile\n@@ -1,7 +1,7 @@\n #checkov:skip=CKV_DOCKER_2:Healthcheck is not relevant for ephemral containers\n #checkov:skip=CKV_DOCKER_3:User is created automatically by lambda runtime\n FROM public.ecr.aws/lambda/python:3.9\n-ENV AWS_ACCESS_KEY_ID=\"wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY\"\n+ENV AWS_ACCESS_KEY_ID=\"AKIAZZZZZZZZZZZZZZZZ\"\n ENV PIP_ENV_VERSION=\"2022.1.8\"\n \n \n"
            },
        "7dff3b21fc2563f51655f34f0d3601cdf79d0d5e":
            {
                "Dockerfile": "diff --git a/Dockerfile b/Dockerfile\nindex 0000..0000 0000\n--- a/Dockerfile\n+++ b/Dockerfile\n@@ -1,7 +1,7 @@\n #checkov:skip=CKV_DOCKER_2:Healthcheck is not relevant for ephemral containers\n #checkov:skip=CKV_DOCKER_3:User is created automatically by lambda runtime\n FROM public.ecr.aws/lambda/python:3.9\n-ENV AWS_ACCESS_KEY_ID=\"AKIAZZZZZZZZZZZZZZZZ\"\n+\n ENV PIP_ENV_VERSION=\"2022.1.8\"\n \n \n"
            },
        "6941281550a12659bdbe87c9a537f88124f78fac":
            {
                "null": "diff --git a/None b/main.py\nindex 0000..0000 0000\n--- a/None\n+++ b/main.py\n@@ -0,0 +1,4 @@\n+AWS_ACCESS_TOKEN=\"AKIAZZZZZZZZZZZZZZZZ\"\n+\n+if __name__ == \"__main__\":\n+    print(AWS_ACCESS_TOKEN)\n\\ No newline at end of file\n"
            }
    }


@mock.patch('checkov.secrets.scan_git_history.get_commits_diff', mock_git_repo_commits)
def test_scan_git_history() -> None:
    valid_dir_path = "test"

    runner = Runner()
    report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                        runner_filter=RunnerFilter(framework=['secrets'], enable_git_history_secret_scan=True))
    assert len(report.failed_checks) == 3
    assert len(report.parsing_errors) == 0
    assert len(report.passed_checks) == 0
    assert len(report.parsing_errors) == 0
    assert len(report.skipped_checks) == 0
    for failed_check in report.failed_checks:
        assert failed_check.added_commit_hash or failed_check.removed_commit_hash


@mock.patch('checkov.secrets.scan_git_history.get_commits_diff', mock_git_repo_commits)
def test_scan_history_secrets() -> None:
    """
    add secret (secret1 added) - +1
    move the secret to different line - 0
    modify the secret value (secret1 removed=update + secret2 added) - +1
    remove the secret (secret2 removed=update) - 0
    add file with new secret (secret3 added) - +1
    """
    valid_dir_path = "test"
    secrets = SecretsCollection()
    plugins_used = [
        {'name': 'AWSKeyDetector'},
    ]
    with transient_settings({
        # Only run scans with only these plugins.
        'plugins_used': plugins_used
    }) as settings:
        settings.disable_filters(*['detect_secrets.filters.common.is_invalid_file'])
        scan_history(valid_dir_path, secrets)
    assert len(secrets.data) == 3


def test_scan_git_history_merge_added_removed() -> None:
    """
    add, move, remove, add, move = secret with the first commit for add and not removed commit
    """
    valid_dir_path = "/Users/lshindelman/development/test2"

    runner = Runner()
    report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                        runner_filter=RunnerFilter(framework=['secrets'], enable_git_history_secret_scan=True))
    assert len(report.failed_checks) == 1
    assert len(report.parsing_errors) == 0
    assert len(report.passed_checks) == 0
    assert len(report.parsing_errors) == 0
    assert len(report.skipped_checks) == 0
    for failed_check in report.failed_checks:
        assert failed_check.added_commit_hash or failed_check.removed_commit_hash
