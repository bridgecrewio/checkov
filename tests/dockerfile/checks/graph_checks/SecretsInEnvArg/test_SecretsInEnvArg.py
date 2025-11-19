import os
from checkov.dockerfile.runner import Runner


def test_secrets_in_env_arg_check():
    """
    Validate CKV_DOCKER_1005 detects secrets in ENV/ARG instructions
    """
    test_dir = os.path.dirname(__file__)
    report = Runner().run(root_folder=test_dir)

    failed_checks = [check for check in report.failed_checks if check.check_id == "CKV_DOCKER_1005"]
    passed_checks = [check for check in report.passed_checks if check.check_id == "CKV_DOCKER_1005"]

    assert failed_checks, "Expected at least one failed check for secrets in ENV/ARG"
    assert passed_checks, "Expected at least one passed check for secrets in ENV/ARG"


def test_private_key_detection():
    """
    Ensure CKV_DOCKER_1005 detects private key exposure in ENV variables
    """
    test_dir = os.path.dirname(__file__)
    report = Runner().run(root_folder=test_dir)
    fail_files = [check.file_path for check in report.failed_checks]

    assert any("Dockerfile.privatekey.fail" in f for f in fail_files), \
        "Expected private key pattern to be detected"

