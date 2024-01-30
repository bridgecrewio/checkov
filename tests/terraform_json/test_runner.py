from pathlib import Path

import pytest

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.bridgecrew.severities import Severities, BcSeverities
from checkov.common.graph.db_connectors.networkx.networkx_db_connector import NetworkxConnector
from checkov.common.graph.db_connectors.rustworkx.rustworkx_db_connector import RustworkxConnector
from checkov.runner_filter import RunnerFilter
from checkov.terraform_json.runner import TerraformJsonRunner

EXAMPLES_DIR = Path(__file__).parent / "examples"


@pytest.mark.parametrize(
    "graph_connector",
    [
        NetworkxConnector,
        RustworkxConnector,
    ],
)
def test_runner_honors_enforcement_rules(graph_connector):
    # given
    test_file = EXAMPLES_DIR / "cdk.tf.json"

    # when
    filter = RunnerFilter(framework=[CheckType.TERRAFORM_JSON], use_enforcement_rules=True)
    # this is not quite a true test, because the checks don't have severities. However, this shows that the check registry
    # passes the report type properly to RunnerFilter.should_run_check, and we have tests for that method
    filter.enforcement_rule_configs = {CheckType.TERRAFORM_JSON: Severities[BcSeverities.OFF]}
    report = TerraformJsonRunner(db_connector=graph_connector()).run(files=[str(test_file)], runner_filter=filter)

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
    test_file = EXAMPLES_DIR / "cdk.tf.json"

    # when
    report = TerraformJsonRunner(db_connector=graph_connector()).run(
        root_folder="", files=[str(test_file)], runner_filter=RunnerFilter(checks=["CKV_AWS_41", "CKV_AWS_21"])
    )

    # then
    summary = report.get_summary()

    assert summary["passed"] == 2
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
    test_file = EXAMPLES_DIR / "cdk.tf.json"

    # when
    report = TerraformJsonRunner(db_connector=graph_connector()).run(
        root_folder="", files=[str(test_file)], runner_filter=RunnerFilter(checks=["CKV2_AWS_6"])
    )

    # then
    summary = report.get_summary()

    assert summary["passed"] == 0
    assert summary["failed"] == 1
    assert summary["skipped"] == 0
    assert summary["parsing_errors"] == 0
