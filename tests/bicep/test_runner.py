from pathlib import Path

import pytest

from checkov.bicep.runner import Runner
from checkov.arm.runner import Runner as ArmRunner
from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.bridgecrew.severities import Severities, BcSeverities
from checkov.common.graph.db_connectors.networkx.networkx_db_connector import NetworkxConnector
from checkov.common.graph.db_connectors.rustworkx.rustworkx_db_connector import RustworkxConnector
from checkov.runner_filter import RunnerFilter
from checkov.bicep.checks.resource.registry import registry as resource_registry
from checkov.bicep.checks.param.registry import registry as param_registry

EXAMPLES_DIR = Path(__file__).parent / "examples"


@pytest.fixture(autouse=True)
def load_arm_checks():
    # just initialize to add the ARM checks to the Bicep registry
    ArmRunner()


def test_registry_has_type():
    assert resource_registry.report_type == CheckType.BICEP
    assert param_registry.report_type == CheckType.BICEP


def test_arm_checks_laoded():
    # when
    resource_registry = Runner.block_type_registries["resources"]

    # then
    assert len(resource_registry.checks) > 30


@pytest.mark.parametrize(
    "graph_connector",
    [
        NetworkxConnector,
        RustworkxConnector
    ]
)
def test_runner_passing_check(graph_connector):
    # given
    test_file = EXAMPLES_DIR / "playground.bicep"

    # when
    report = Runner(db_connector=graph_connector()).run(root_folder="", files=[str(test_file)], runner_filter=RunnerFilter(checks=["CKV_AZURE_3"]))

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
        RustworkxConnector
    ]
)
def test_runner_failing_check(graph_connector):
    # given
    test_file = EXAMPLES_DIR / "playground.bicep"

    # when
    report = Runner(db_connector=graph_connector()).run(root_folder="", files=[str(test_file)], runner_filter=RunnerFilter(checks=["CKV_AZURE_9"]))

    # then
    summary = report.get_summary()

    assert summary["passed"] == 1
    assert summary["failed"] == 1
    assert summary["skipped"] == 0
    assert summary["parsing_errors"] == 0

@pytest.mark.parametrize(
    "graph_connector",
    [
        NetworkxConnector,
        RustworkxConnector
    ]
)
def test_runner_skipping_check(graph_connector):
    # given
    test_file = EXAMPLES_DIR / "playground.bicep"

    # when
    report = Runner(db_connector=graph_connector()).run(root_folder="", files=[str(test_file)], runner_filter=RunnerFilter(checks=["CKV_AZURE_35"]))

    # then
    summary = report.get_summary()

    assert summary["passed"] == 0
    assert summary["failed"] == 0
    assert summary["skipped"] == 1
    assert summary["parsing_errors"] == 0

@pytest.mark.parametrize(
    "graph_connector",
    [
        NetworkxConnector,
        RustworkxConnector
    ]
)
def test_runner_honors_enforcement_rules(graph_connector):
    # given
    test_files = list(map(lambda f: str(f), [EXAMPLES_DIR / "playground.bicep", EXAMPLES_DIR / "graph.bicep"]))

    # when
    filter = RunnerFilter(framework=['bicep'], use_enforcement_rules=True)
    # this is not quite a true test, because the checks don't have severities. However, this shows that the check registry
    # passes the report type properly to RunnerFilter.should_run_check, and we have tests for that method
    filter.enforcement_rule_configs = {CheckType.BICEP: Severities[BcSeverities.OFF]}
    report = Runner(db_connector=graph_connector()).run(root_folder="", files=test_files, runner_filter=filter)

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
        RustworkxConnector
    ]
)
def test_runner_parsing_errors(graph_connector):
    # given
    test_file = EXAMPLES_DIR / "malformed.bicep"

    # when
    report = Runner(db_connector=graph_connector()).run(root_folder="", files=[str(test_file)], runner_filter=RunnerFilter(checks=["CKV_AZURE_35"]))

    # then
    summary = report.get_summary()

    assert summary["passed"] == 0
    assert summary["failed"] == 0
    assert summary["skipped"] == 0
    assert summary["parsing_errors"] == 1

@pytest.mark.parametrize(
    "graph_connector",
    [
        NetworkxConnector,
        RustworkxConnector
    ]
)
def test_runner_ignore_existing_resource(graph_connector):
    # given
    test_file = EXAMPLES_DIR / "existing.bicep"

    # when
    report = Runner(db_connector=graph_connector()).run(root_folder="", files=[str(test_file)], runner_filter=RunnerFilter(checks=["CKV_AZURE_35"]))

    # then
    summary = report.get_summary()

    assert summary["passed"] == 0
    assert summary["failed"] == 1
    assert summary["skipped"] == 0
    assert summary["parsing_errors"] == 0
    assert summary["resource_count"] == 2  # 1 should be unknown

    assert report.failed_checks[0].resource == "Microsoft.Storage/storageAccounts.storageAccount"

@pytest.mark.parametrize(
    "graph_connector",
    [
        NetworkxConnector,
        RustworkxConnector
    ]
)
def test_runner_extra_resources(graph_connector):
    # given
    test_file = EXAMPLES_DIR / "playground.bicep"

    # when
    report = Runner(db_connector=graph_connector()).run(root_folder="", files=[str(test_file)], runner_filter=RunnerFilter(checks=["CKV_AZURE_3"]))

    # then
    summary = report.get_summary()

    assert summary["passed"] == 1

    assert len(report.extra_resources) == 7
    extra_resource = next(
        resource for resource in report.extra_resources if resource.resource == "Microsoft.Compute/virtualMachines.vm"
    )
    assert extra_resource.file_abs_path == str(test_file)
    assert extra_resource.file_path.endswith("playground.bicep")


def test_runner_loop_resource():
    # given
    test_file = EXAMPLES_DIR / "loop.bicep"

    # when
    report = Runner().run(root_folder="", files=[str(test_file)], runner_filter=RunnerFilter(checks=["CKV_AZURE_2"]))

    # then
    summary = report.get_summary()

    assert summary["passed"] == 1
    assert summary["failed"] == 0
    assert summary["skipped"] == 0
    assert summary["parsing_errors"] == 0
