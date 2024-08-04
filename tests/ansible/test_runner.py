from pathlib import Path

import pytest

from checkov.ansible.checks.registry import registry
from checkov.ansible.runner import Runner
from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.bridgecrew.severities import Severities, BcSeverities
from checkov.common.graph.db_connectors.networkx.networkx_db_connector import NetworkxConnector
from checkov.common.graph.db_connectors.rustworkx.rustworkx_db_connector import RustworkxConnector
from checkov.runner_filter import RunnerFilter

EXAMPLES_DIR = Path(__file__).parent / "examples"


def test_registry_has_type():
    assert registry.report_type == CheckType.ANSIBLE


@pytest.mark.parametrize(
    "graph_connector",
    [
        NetworkxConnector,
        RustworkxConnector,
    ],
)
def test_runner_honors_enforcement_rules(graph_connector):
    # given
    test_file = EXAMPLES_DIR / "site.yml"

    # when
    filter = RunnerFilter(framework=["ansible"], use_enforcement_rules=True)
    # this is not quite a true test, because the checks don't have severities. However, this shows that the check registry
    # passes the report type properly to RunnerFilter.should_run_check, and we have tests for that method
    filter.enforcement_rule_configs = {CheckType.ANSIBLE: Severities[BcSeverities.OFF]}
    report = Runner(db_connector=graph_connector()).run(root_folder="", files=[str(test_file)], runner_filter=filter)

    # then
    summary = report.get_summary()

    assert summary["passed"] == 0
    assert summary["failed"] == 0
    assert summary["skipped"] == 0
    assert summary["parsing_errors"] == 0


@pytest.mark.parametrize(
    "graph_connector",
    [
        NetworkxConnector,
        RustworkxConnector,
    ],
)
def test_runner_passing_check(graph_connector):
    # given
    test_file = EXAMPLES_DIR / "site.yml"

    # when
    report = Runner(db_connector=graph_connector()).run(
        root_folder="", files=[str(test_file)], runner_filter=RunnerFilter(checks=["CKV_AWS_135"])
    )

    # then
    summary = report.get_summary()

    assert summary["passed"] == 1
    assert summary["failed"] == 0
    assert summary["skipped"] == 0
    assert summary["parsing_errors"] == 0


@pytest.mark.parametrize(
    "graph_connector",
    [
        NetworkxConnector,
        RustworkxConnector,
    ],
)
def test_runner_failing_check(graph_connector):
    # given
    test_file = EXAMPLES_DIR / "site.yml"

    # when
    report = Runner(db_connector=graph_connector()).run(
        root_folder="", files=[str(test_file)], runner_filter=RunnerFilter(checks=["CKV_AWS_88"])
    )

    # then
    summary = report.get_summary()

    assert summary["passed"] == 0
    assert summary["failed"] == 1
    assert summary["skipped"] == 0
    assert summary["parsing_errors"] == 0


@pytest.mark.parametrize(
    "graph_connector",
    [
        NetworkxConnector,
        RustworkxConnector,
    ],
)
def test_runner_skipping_check(graph_connector):
    # given
    test_file = EXAMPLES_DIR / "skip.yml"

    # when
    report = Runner(db_connector=graph_connector()).run(
        root_folder="",
        files=[str(test_file)],
        runner_filter=RunnerFilter(checks=["CKV2_ANSIBLE_1", "CKV_AWS_88", "CKV_AWS_135"]),
    )

    # then
    summary = report.get_summary()

    assert summary["passed"] == 0
    assert summary["failed"] == 2
    assert summary["skipped"] == 3
    assert summary["parsing_errors"] == 0

    assert {check.check_id for check in report.skipped_checks} == {"CKV2_ANSIBLE_1", "CKV_AWS_88", "CKV_AWS_135"}

    ansible_1 = next(check for check in report.skipped_checks if check.check_id == "CKV2_ANSIBLE_1")
    aws_88 = next(check for check in report.skipped_checks if check.check_id == "CKV_AWS_88")
    aws_135 = next(check for check in report.skipped_checks if check.check_id == "CKV_AWS_135")
    assert ansible_1.resource == "tasks.uri.http"
    assert aws_88.resource == "tasks.amazon.aws.ec2_instance.Launch ec2 instances 2"
    assert aws_135.resource == "tasks.amazon.aws.ec2_instance.Launch ec2 instances 1"


@pytest.mark.parametrize(
    "graph_connector",
    [
        NetworkxConnector,
        RustworkxConnector,
    ],
)
def test_runner_with_flat_tasks(graph_connector):
    # given
    test_file = EXAMPLES_DIR / "tasks.yml"

    # when
    report = Runner(db_connector=graph_connector()).run(
        root_folder="", files=[str(test_file)], runner_filter=RunnerFilter(checks=["CKV_ANSIBLE_1", "CKV_ANSIBLE_2"])
    )

    # then
    summary = report.get_summary()

    assert summary["passed"] == 1
    assert summary["failed"] == 1
    assert summary["skipped"] == 0
    assert summary["parsing_errors"] == 0

    passing_resources = {
        f"tasks.uri.Check that you can connect (GET) to a page",
    }

    failing_resources = {
        f"tasks.ansible.builtin.get_url.Download foo.conf",
    }

    passed_check_resources = {check.resource for check in report.passed_checks}
    failed_check_resources = {check.resource for check in report.failed_checks}

    assert passing_resources == passed_check_resources
    assert failing_resources == failed_check_resources


@pytest.mark.parametrize(
    "graph_connector",
    [
        NetworkxConnector,
        RustworkxConnector,
    ],
)
def test_runner_with_block(graph_connector):
    # given
    test_file = EXAMPLES_DIR / "blocks.yml"
    checks = ["CKV_ANSIBLE_3", "CKV_ANSIBLE_4", "CKV2_ANSIBLE_3"]

    # when
    report = Runner(db_connector=graph_connector()).run(
        root_folder="", files=[str(test_file)], runner_filter=RunnerFilter(checks=checks)
    )

    # then
    summary = report.get_summary()

    assert summary["passed"] == 1
    assert summary["failed"] == 2
    assert summary["skipped"] == 0
    assert summary["parsing_errors"] == 0

    passing_resources = {
        "tasks.block.ansible.builtin.yum.Install httpd and memcached",
    }

    failing_resources = {
        "tasks.block.ansible.builtin.yum.Install httpd and memcached",
        "block.Install, configure, and start Apache",
    }

    passed_check_resources = {check.resource for check in report.passed_checks}
    failed_check_resources = {check.resource for check in report.failed_checks}

    assert passing_resources == passed_check_resources
    assert failing_resources == failed_check_resources


@pytest.mark.parametrize(
    "graph_connector",
    [
        NetworkxConnector,
        RustworkxConnector,
    ],
)
def test_runner_with_nested_blocks(graph_connector):
    # given
    test_file = EXAMPLES_DIR / "nested_blocks.yml"
    checks = ["CKV_ANSIBLE_1", "CKV2_ANSIBLE_3"]

    # when
    report = Runner(db_connector=graph_connector()).run(
        root_folder="", files=[str(test_file)], runner_filter=RunnerFilter(checks=checks)
    )

    # then
    summary = report.get_summary()

    # if we increase the level of nested block levels for Python checks, then this goes up to 6
    assert summary["passed"] == 4
    assert summary["failed"] == 5
    assert summary["skipped"] == 0
    assert summary["parsing_errors"] == 0

    passing_resources = {
        "tasks.ansible.builtin.uri.1st level uri",
        "tasks.block.ansible.builtin.uri.2nd level uri",
        "tasks.block.block.ansible.builtin.uri.3rd level uri",
        "tasks.block.block.block.ansible.builtin.uri.4th level uri",
    }

    failing_resources = {
        "block.1st level block",
        "block.block.2nd level block",
        "block.block.block.3rd level block",
        "block.block.block.block.4th level block",
        "block.block.block.block.block.5th level block",
    }

    passed_check_resources = {check.resource for check in report.passed_checks}
    failed_check_resources = {check.resource for check in report.failed_checks}

    assert passing_resources == passed_check_resources
    assert failing_resources == failed_check_resources


@pytest.mark.parametrize(
    "graph_connector",
    [
        NetworkxConnector,
        RustworkxConnector,
    ],
)
def test_runner_with_no_tasks(graph_connector):
    # given
    test_file = EXAMPLES_DIR / "no_tasks.yml"

    # when
    report = Runner(db_connector=graph_connector()).run(root_folder="", files=[str(test_file)])

    # then
    summary = report.get_summary()

    assert summary["passed"] == 0
    assert summary["failed"] == 0
    assert summary["skipped"] == 0
    assert summary["parsing_errors"] == 0


@pytest.mark.parametrize(
    "graph_connector",
    [
        NetworkxConnector,
        RustworkxConnector,
    ],
)
def test_get_resource(graph_connector):
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
    runner = Runner(db_connector=graph_connector())
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
    assert new_key == "tasks.amazon.aws.ec2_instance.enabled"


@pytest.mark.parametrize(
    "graph_connector",
    [
        NetworkxConnector,
        RustworkxConnector,
    ],
)
def test_get_resource_without_name(graph_connector):
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
    runner = Runner(db_connector=graph_connector())
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
    assert new_key == "tasks.amazon.aws.ec2_instance.unknown"


def test_runner_process_utf16_file():
    # given
    test_file = EXAMPLES_DIR / "k8s_utf16.yaml"

    # when
    report = Runner().run(root_folder="", files=[str(test_file)])

    # then
    summary = report.get_summary()

    assert summary["passed"] == 0
    assert summary["failed"] == 0
    assert summary["skipped"] == 0
    assert summary["parsing_errors"] == 0
