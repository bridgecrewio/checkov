from pathlib import Path

from checkov.github_actions.runner import Runner
from checkov.runner_filter import RunnerFilter

EXTRA_YAML_CHECKS_DIR = Path(__file__).parent / "extra_yaml_checks"
RESOURCES_DIR = Path(__file__).parent.parent / "resources"


def test_simple_attribute_check():
    # given
    test_file = str(RESOURCES_DIR / ".github/workflows/slsa-gen.yaml")
    runner = Runner()

    # when
    report = runner.run(
        files=[test_file],
        external_checks_dir=[str(EXTRA_YAML_CHECKS_DIR)],
        runner_filter=RunnerFilter(checks="CKV2_GHA_CUSTOM_1"),
    )

    # remove all checks
    runner.graph_registry.checks.clear()

    # then
    summary = report.get_summary()

    passing_resources = {
        "jobs(build)",
        "jobs(scan)",
    }
    failing_resources = {
        "jobs(attest)",
        "jobs(provenance)",
    }

    passed_check_resources = {c.resource for c in report.passed_checks}
    failed_check_resources = {c.resource for c in report.failed_checks}

    assert summary["passed"] == len(passing_resources)
    assert summary["failed"] == len(failing_resources)
    assert summary["skipped"] == 0
    assert summary["parsing_errors"] == 0

    assert passed_check_resources == passing_resources
    assert failed_check_resources == failing_resources


def test_jobs_steps_connection_check():
    # given
    test_file = str(RESOURCES_DIR / ".github/workflows/slsa-gen.yaml")
    runner = Runner()

    # when
    report = runner.run(
        files=[test_file],
        external_checks_dir=[str(EXTRA_YAML_CHECKS_DIR)],
        runner_filter=RunnerFilter(checks="CKV2_GHA_CUSTOM_2"),
    )

    # remove all checks
    runner.graph_registry.checks.clear()

    # then
    summary = report.get_summary()

    failing_resources = {
        "jobs(attest).steps[6](Log in to GHCR)",
    }

    failed_check_resources = {c.resource for c in report.failed_checks}

    assert summary["passed"] == 18
    assert summary["failed"] == len(failing_resources)
    assert summary["skipped"] == 0
    assert summary["parsing_errors"] == 0

    assert failed_check_resources == failing_resources


def test_on_check():
    # given
    test_file = str(RESOURCES_DIR / ".github/workflows/workflow_with_image.yml")
    runner = Runner()

    # when
    report = runner.run(
        files=[test_file],
        external_checks_dir=[str(EXTRA_YAML_CHECKS_DIR)],
        runner_filter=RunnerFilter(checks="CKV2_GHA_CUSTOM_3"),
    )

    # remove all checks
    runner.graph_registry.checks.clear()

    # then
    summary = report.get_summary()


    passing_resources = {
        "on(CI)",
    }

    passed_check_resources = {c.resource for c in report.passed_checks}

    assert summary["passed"] == len(passing_resources)
    assert summary["failed"] == 0
    assert summary["skipped"] == 0
    assert summary["parsing_errors"] == 0

    assert passed_check_resources == passing_resources
