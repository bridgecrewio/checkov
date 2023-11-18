from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from checkov.kubernetes.runner import Runner
from checkov.runner_filter import RunnerFilter
from tests.graph_utils.utils import GRAPH_FRAMEWORKS

RESOURCES_DIR = Path(__file__).parent / "resources"


@pytest.mark.parametrize("graph_framework", GRAPH_FRAMEWORKS)
def test_runner(mocker: MockerFixture, graph_framework):
    # given
    test_file_path = RESOURCES_DIR / "graph_check.yaml"
    runner_filter = RunnerFilter(checks=["CKV2_K8S_6"])

    mocker.patch.dict("os.environ", {"CHECKOV_GRAPH_FRAMEWORK": graph_framework})

    # when
    report = Runner().run(root_folder=None, files=[str(test_file_path)], runner_filter=runner_filter)

    #  when
    summary = report.get_summary()

    assert summary["passed"] == 1
    assert summary["failed"] == 1
    assert summary["skipped"] == 1
    assert summary["parsing_errors"] == 0
