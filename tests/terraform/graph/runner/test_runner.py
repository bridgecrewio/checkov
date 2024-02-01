from pathlib import Path

import pytest

from checkov.common.graph.db_connectors.networkx.networkx_db_connector import NetworkxConnector
from checkov.common.graph.db_connectors.rustworkx.rustworkx_db_connector import RustworkxConnector
from checkov.runner_filter import RunnerFilter
from checkov.terraform.runner import Runner

@pytest.mark.parametrize(
    "graph_connector",
    [
        NetworkxConnector,
        RustworkxConnector
    ]
)
def test_dynamics(graph_connector):
    # given
    test_files_dir = Path(__file__).parent.parent / "resources/dynamic_lambda_function"

    # when
    report = Runner(db_connector=graph_connector()).run(
        root_folder=str(test_files_dir),
        runner_filter=RunnerFilter(
            checks=[
                "CKV_AWS_45",
                "CKV_AWS_116",
                "CKV_AWS_173",
                "CKV_AWS_272",
            ]
        ),
    )

    # then
    summary = report.get_summary()

    assert summary["passed"] == 2
    assert summary["failed"] == 2
    assert summary["skipped"] == 0
    assert summary["parsing_errors"] == 0
