from typing import Dict
from unittest import mock

from detect_secrets import SecretsCollection

from checkov.secrets.scan_git_history import scan_history
from checkov.secrets.runner import Runner
from checkov.runner_filter import RunnerFilter
from detect_secrets.settings import transient_settings


def mock_git_repo_commits(root_folder: str) -> Dict[str, Dict[str, str]]:
    """
        add secret (secret1 added) - +1
        move the secret to different line - 0
        modify the secret value (secret1 removed=update + secret2 added) - +1
        remove the secret (secret2 removed=update) - 0
        add file with new secret (secret3 added) - +1
    """
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


def mock_git_repo_commits2(root_folder: str) -> Dict[str, Dict[str, str]]:
    """
        add secret (secret1 added) - +1
        move the secret to different line - 0
        remove the secret (secret1 removed=update) - 0
        add secret (secret1 added - add the same secret - update) - 0
        move the secret to different line - 0
    """
    return {
        "11e59e4e578c6ebcb48aae1e5e078a54c62920eb": {
            "folder1/folder2/Dockerfile": "diff --git a/folder1/folder2/Dockerfile b/folder1/folder2/Dockerfile\nindex 0000..0000 0000\n--- a/folder1/folder2/Dockerfile\n+++ b/folder1/folder2/Dockerfile\n@@ -5,7 +5,7 @@ FROM public.ecr.aws/lambda/python:3.9\n \n ENV PIP_ENV_VERSION=\"2022.1.8\"\n COPY Pipfile Pipfile.lock ./\n-\n+ENV AWS_ACCESS_KEY_ID=\"wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY\"\n \n RUN pip install pipenv==${PIP_ENV_VERSION} \\\n  && pipenv lock -r > requirements.txt \\\n"
        },
        "c7c932ef4d31c487a921d2ce8544a4a468adf6b9": {
            "folder1/folder2/Dockerfile": "diff --git a/folder1/folder2/Dockerfile b/folder1/folder2/Dockerfile\nindex 0000..0000 0000\n--- a/folder1/folder2/Dockerfile\n+++ b/folder1/folder2/Dockerfile\n@@ -2,10 +2,10 @@\n #checkov:skip=CKV_DOCKER_3:User is created automatically by lambda runtime\n FROM public.ecr.aws/lambda/python:3.9\n \n-\n+ENV AWS_ACCESS_KEY_ID=\"wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY\"\n ENV PIP_ENV_VERSION=\"2022.1.8\"\n COPY Pipfile Pipfile.lock ./\n-ENV AWS_ACCESS_KEY_ID=\"wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY\"\n+\n \n RUN pip install pipenv==${PIP_ENV_VERSION} \\\n  && pipenv lock -r > requirements.txt \\\n"
        },
        "4b8321e46217a87e21240afd88cdc0f1a861c0f5": {
            "folder1/folder2/Dockerfile": "diff --git a/folder1/folder2/Dockerfile b/folder1/folder2/Dockerfile\nindex 0000..0000 0000\n--- a/folder1/folder2/Dockerfile\n+++ b/folder1/folder2/Dockerfile\n@@ -2,7 +2,6 @@\n #checkov:skip=CKV_DOCKER_3:User is created automatically by lambda runtime\n FROM public.ecr.aws/lambda/python:3.9\n \n-ENV AWS_ACCESS_KEY_ID=\"wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY\"\n ENV PIP_ENV_VERSION=\"2022.1.8\"\n COPY Pipfile Pipfile.lock ./\n \n"
        },
        "7bb5c69d95b31bc2242bcf08ce25e74e953f9ae9": {
            "folder1/folder2/Dockerfile": "diff --git a/folder1/folder2/Dockerfile b/folder1/folder2/Dockerfile\nindex 0000..0000 0000\n--- a/folder1/folder2/Dockerfile\n+++ b/folder1/folder2/Dockerfile\n@@ -4,7 +4,7 @@ FROM public.ecr.aws/lambda/python:3.9\n \n ENV PIP_ENV_VERSION=\"2022.1.8\"\n COPY Pipfile Pipfile.lock ./\n-\n+ENV AWS_ACCESS_KEY_ID=\"wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY\"\n \n RUN pip install pipenv==${PIP_ENV_VERSION} \\\n  && pipenv lock -r > requirements.txt \\\n"
        },
        "2675bffd2662aae7025b7f3bb5fd384cdab355b1": {
            "folder1/folder2/Dockerfile": "diff --git a/folder1/folder2/Dockerfile b/folder1/folder2/Dockerfile\nindex 0000..0000 0000\n--- a/folder1/folder2/Dockerfile\n+++ b/folder1/folder2/Dockerfile\n@@ -1,10 +1,11 @@\n #checkov:skip=CKV_DOCKER_2:Healthcheck is not relevant for ephemral containers\n #checkov:skip=CKV_DOCKER_3:User is created automatically by lambda runtime\n FROM public.ecr.aws/lambda/python:3.9\n+ENV AWS_ACCESS_KEY_ID=\"wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY\"\n \n ENV PIP_ENV_VERSION=\"2022.1.8\"\n COPY Pipfile Pipfile.lock ./\n-ENV AWS_ACCESS_KEY_ID=\"wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY\"\n+\n \n RUN pip install pipenv==${PIP_ENV_VERSION} \\\n  && pipenv lock -r > requirements.txt \\\n"
        }
    }


def mock_git_repo_commits3(root_folder: str) -> Dict[str, Dict[str, str]]:
    """
            add secret (secret1 added) - +1
            move the secret to different line - 0
            add secret equal to secret1 - +1
            remove one secret (secret1 - update add remove_commit_hash) - 0
        """
    return {
        "900b1e8f6f336a92e8f5fca3babca764e32c3b3d": {
            "folder1/folder2/Dockerfile": "diff --git a/folder1/folder2/Dockerfile b/folder1/folder2/Dockerfile\nindex 0000..0000 0000\n--- a/folder1/folder2/Dockerfile\n+++ b/folder1/folder2/Dockerfile\n@@ -1,6 +1,7 @@\n #checkov:skip=CKV_DOCKER_2:Healthcheck is not relevant for ephemral containers\n #checkov:skip=CKV_DOCKER_3:User is created automatically by lambda runtime\n FROM public.ecr.aws/lambda/python:3.9\n+ENV AWS_ACCESS_KEY_ID=\"AKIAZZZZZZZZZZZZZZZZ\"\n \n ENV PIP_ENV_VERSION=\"2022.1.8\"\n COPY Pipfile Pipfile.lock ./\n"
        },
        "4229974aec78152c426b40db8b6912ba098f3add": {
            "folder1/folder2/Dockerfile": "diff --git a/folder1/folder2/Dockerfile b/folder1/folder2/Dockerfile\nindex 0000..0000 0000\n--- a/folder1/folder2/Dockerfile\n+++ b/folder1/folder2/Dockerfile\n@@ -1,11 +1,11 @@\n #checkov:skip=CKV_DOCKER_2:Healthcheck is not relevant for ephemral containers\n #checkov:skip=CKV_DOCKER_3:User is created automatically by lambda runtime\n FROM public.ecr.aws/lambda/python:3.9\n-ENV AWS_ACCESS_KEY_ID=\"AKIAZZZZZZZZZZZZZZZZ\"\n+\n \n ENV PIP_ENV_VERSION=\"2022.1.8\"\n COPY Pipfile Pipfile.lock ./\n-\n+ENV AWS_ACCESS_KEY_ID=\"AKIAZZZZZZZZZZZZZZZZ\"\n \n RUN pip install pipenv==${PIP_ENV_VERSION} \\\n  && pipenv lock -r > requirements.txt \\\n"
        },
        "3c8cb7eedb3986308c96713fc65b006adcf3bc44": {
            "folder1/folder2/Dockerfile": "diff --git a/folder1/folder2/Dockerfile b/folder1/folder2/Dockerfile\nindex 0000..0000 0000\n--- a/folder1/folder2/Dockerfile\n+++ b/folder1/folder2/Dockerfile\n@@ -6,7 +6,7 @@ FROM public.ecr.aws/lambda/python:3.9\n ENV PIP_ENV_VERSION=\"2022.1.8\"\n COPY Pipfile Pipfile.lock ./\n ENV AWS_ACCESS_KEY_ID=\"AKIAZZZZZZZZZZZZZZZZ\"\n-\n+ENV AWS_ACCESS_KEY_ID=\"AKIAZZZZZZZZZZZZZZZZ\"\n RUN pip install pipenv==${PIP_ENV_VERSION} \\\n  && pipenv lock -r > requirements.txt \\\n  && pipenv run pip install -r requirements.txt --target \"${LAMBDA_TASK_ROOT}\" \\\n"
        },
        "697308e61171e33224757e620aaf67b1a877c99d": {
            "folder1/folder2/Dockerfile": "diff --git a/folder1/folder2/Dockerfile b/folder1/folder2/Dockerfile\nindex 0000..0000 0000\n--- a/folder1/folder2/Dockerfile\n+++ b/folder1/folder2/Dockerfile\n@@ -5,7 +5,7 @@ FROM public.ecr.aws/lambda/python:3.9\n \n ENV PIP_ENV_VERSION=\"2022.1.8\"\n COPY Pipfile Pipfile.lock ./\n-ENV AWS_ACCESS_KEY_ID=\"AKIAZZZZZZZZZZZZZZZZ\"\n+\n ENV AWS_ACCESS_KEY_ID=\"AKIAZZZZZZZZZZZZZZZZ\"\n RUN pip install pipenv==${PIP_ENV_VERSION} \\\n  && pipenv lock -r > requirements.txt \\\n"
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


@mock.patch('checkov.secrets.scan_git_history.get_commits_diff', mock_git_repo_commits2)
def test_scan_git_history_merge_added_removed() -> None:
    """
    add, move, remove, add, move = secret with the first added_commit_hash and not removed_commit_hash
    """
    valid_dir_path = "test"

    runner = Runner()
    report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                        runner_filter=RunnerFilter(framework=['secrets'], enable_git_history_secret_scan=True))
    assert len(report.failed_checks) == 1
    for failed_check in report.failed_checks:
        assert failed_check.removed_commit_hash is None
        assert failed_check.added_commit_hash == '11e59e4e578c6ebcb48aae1e5e078a54c62920eb'


@mock.patch('checkov.secrets.scan_git_history.get_commits_diff', mock_git_repo_commits2)
def test_scan_history_secrets_merge_added_removed() -> None:
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
    assert len(secrets.data) == 1


@mock.patch('checkov.secrets.scan_git_history.get_commits_diff', mock_git_repo_commits3)
def test_scan_git_history_merge_added_removed2() -> None:
    """
        add, move, add, remove one = 2 secret one with removed_commit_hash && added_commit_hash
        and one with only added_commit_hash
    """
    valid_dir_path = "/Users/lshindelman/development/test2"

    runner = Runner()
    report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                        runner_filter=RunnerFilter(framework=['secrets'], enable_git_history_secret_scan=True))
    assert len(report.failed_checks) == 2
    assert ((report.failed_checks[0].removed_commit_hash == '697308e61171e33224757e620aaf67b1a877c99d'
            and report.failed_checks[1].removed_commit_hash is None)
            or (report.failed_checks[1].removed_commit_hash == '697308e61171e33224757e620aaf67b1a877c99d'
            and report.failed_checks[0].removed_commit_hash is None))
    assert ((report.failed_checks[0].added_commit_hash == '900b1e8f6f336a92e8f5fca3babca764e32c3b3d'
            and report.failed_checks[1].added_commit_hash == '3c8cb7eedb3986308c96713fc65b006adcf3bc44')
            or (report.failed_checks[1].added_commit_hash == '900b1e8f6f336a92e8f5fca3babca764e32c3b3d'
            and report.failed_checks[0].added_commit_hash == '3c8cb7eedb3986308c96713fc65b006adcf3bc44'))

