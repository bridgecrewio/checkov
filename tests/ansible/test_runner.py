from pathlib import Path

from checkov.ansible.checks.registry import registry
from checkov.ansible.runner import Runner
from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.bridgecrew.severities import Severities, BcSeverities
from checkov.runner_filter import RunnerFilter

EXAMPLES_DIR = Path(__file__).parent / "examples"


def test_registry_has_type():
    assert registry.report_type == CheckType.ANSIBLE


def test_runner_honors_enforcement_rules():
    # given
    test_file = EXAMPLES_DIR / "site.yml"

    # when
    filter = RunnerFilter(framework=["ansible"], use_enforcement_rules=True)
    # this is not quite a true test, because the checks don't have severities. However, this shows that the check registry
    # passes the report type properly to RunnerFilter.should_run_check, and we have tests for that method
    filter.enforcement_rule_configs = {CheckType.ANSIBLE: Severities[BcSeverities.OFF]}
    report = Runner().run(root_folder="", files=[str(test_file)], runner_filter=filter)

    # then
    summary = report.get_summary()

    assert summary["passed"] == 0
    assert summary["failed"] == 0
    assert summary["skipped"] == 0
    assert summary["parsing_errors"] == 0


def test_runner_passing_check():
    # given
    test_file = EXAMPLES_DIR / "site.yml"

    # when
    report = Runner().run(root_folder="", files=[str(test_file)], runner_filter=RunnerFilter(checks=["CKV_AWS_135"]))

    # then
    summary = report.get_summary()

    assert summary["passed"] == 1
    assert summary["failed"] == 0
    assert summary["skipped"] == 0
    assert summary["parsing_errors"] == 0


def test_runner_failing_check():
    # given
    test_file = EXAMPLES_DIR / "site.yml"

    # when
    report = Runner().run(root_folder="", files=[str(test_file)], runner_filter=RunnerFilter(checks=["CKV_AWS_88"]))

    # then
    summary = report.get_summary()

    assert summary["passed"] == 0
    assert summary["failed"] == 1
    assert summary["skipped"] == 0
    assert summary["parsing_errors"] == 0


def test_runner_with_flat_tasks():
    # given
    test_file = EXAMPLES_DIR / "tasks.yml"

    # when
    report = Runner().run(
        root_folder="", files=[str(test_file)], runner_filter=RunnerFilter(checks=["CKV_ANSIBLE_1", "CKV_ANSIBLE_2"])
    )

    # then
    summary = report.get_summary()

    assert summary["passed"] == 1
    assert summary["failed"] == 1
    assert summary["skipped"] == 0
    assert summary["parsing_errors"] == 0

    passing_resources = {
        f"task.Check that you can connect (GET) to a page",
    }

    failing_resources = {
        f"task.Download foo.conf",
    }

    passed_check_resources = {check.resource for check in report.passed_checks}
    failed_check_resources = {check.resource for check in report.passed_checks}

    assert passing_resources == passed_check_resources
    assert failing_resources == failed_check_resources


def test_get_resource():
    # given
    file_path = "/example/site.yml"
    key = '[].tasks[?"amazon.aws.ec2_instance" != null][].[].tasks[?"amazon.aws.ec2_instance" != null][].CKV_AWS_135[6:12]'
    start_line = 8
    end_line = 12
    definition = [
        {
            "name": "Verify tests",
            "hosts": "all",
            "gather_facts": False,
            "tasks": [
                {
                    "name": "enabled",
                    "amazon.aws.ec2_instance": {
                        "name": "public-compute-instance",
                        "key_name": "prod-ssh-key",
                        "vpc_subnet_id": "subnet-5ca1ab1e",
                        "instance_type": "c5.large",
                        "security_group": "default",
                        "network": {"assign_public_ip": False, "__startline__": 14, "__endline__": 15},
                        "image_id": "ami-123456",
                        "ebs_optimized": True,
                        "__startline__": 8,
                        "__endline__": 17,
                    },
                    "__startline__": 6,
                    "__endline__": 17,
                }
            ],
            "__startline__": 2,
            "__endline__": 17,
        }
    ]
    runner = Runner()
    runner.definitions = {file_path: definition}

    # when
    new_key = runner.get_resource(
        file_path=file_path,
        key=key,
        supported_entities=[],
        start_line=start_line,
        end_line=end_line,
    )

    # then
    assert new_key == "task.enabled"


def test_get_resource_without_name():
    # given
    file_path = "/example/site.yml"
    key = '[].tasks[?"amazon.aws.ec2_instance" != null][].[].tasks[?"amazon.aws.ec2_instance" != null][].CKV_AWS_135[6:12]'
    start_line = 8
    end_line = 12
    definition = [
        {
            "name": "Verify tests",
            "hosts": "all",
            "gather_facts": False,
            "tasks": [
                {
                    "amazon.aws.ec2_instance": {
                        "name": "public-compute-instance",
                        "key_name": "prod-ssh-key",
                        "vpc_subnet_id": "subnet-5ca1ab1e",
                        "instance_type": "c5.large",
                        "security_group": "default",
                        "network": {"assign_public_ip": False, "__startline__": 14, "__endline__": 15},
                        "image_id": "ami-123456",
                        "ebs_optimized": True,
                        "__startline__": 8,
                        "__endline__": 17,
                    },
                    "__startline__": 6,
                    "__endline__": 17,
                }
            ],
            "__startline__": 2,
            "__endline__": 17,
        }
    ]
    runner = Runner()
    runner.definitions = {file_path: definition}

    # when
    new_key = runner.get_resource(
        file_path=file_path,
        key=key,
        supported_entities=[],
        start_line=start_line,
        end_line=end_line,
    )

    # then
    assert new_key == "task.unknown"
