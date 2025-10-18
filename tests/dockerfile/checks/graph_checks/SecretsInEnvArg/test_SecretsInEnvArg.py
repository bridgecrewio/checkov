import os
from checkov.dockerfile.runner import Runner


def test_secrets_in_env_arg_check():
    """
    Validate CKV_DOCKER_1005 detects secrets in ENV/ARG instructions
    """
    # locate this test's directory
    test_dir = os.path.dirname(__file__)

    # run the Checkov Dockerfile runner
    report = Runner().run(root_folder=test_dir)

    # collect results
    failed_checks = [check for check in report.failed_checks if check.check_id == "CKV_DOCKER_1005"]
    passed_checks = [check for check in report.passed_checks if check.check_id == "CKV_DOCKER_1005"]

    # assertions
    assert failed_checks, "Expected at least one failed check for secrets in ENV/ARG"
    assert passed_checks, "Expected at least one passing check for clean ENV/ARG"

    # optional: verify specific file outcomes
    fail_files = {check.file_path for check in failed_checks}
    pass_files = {check.file_path for check in passed_checks}

    assert any("Dockerfile.fail" in f for f in fail_files)
    assert any("Dockerfile.pass" in f for f in pass_files)

