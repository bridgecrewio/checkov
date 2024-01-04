from pathlib import Path

import pytest
from pytest_mock import MockerFixture

import os
from checkov.kustomize.runner import Runner
from checkov.runner_filter import RunnerFilter
from tests.graph_utils.utils import GRAPH_FRAMEWORKS
from tests.kustomize.utils import kustomize_exists


@pytest.mark.skipif(not kustomize_exists(), reason="kustomize not installed")
@pytest.mark.parametrize("graph_framework", GRAPH_FRAMEWORKS)
def test_runner(mocker: MockerFixture, graph_framework):
    scan_dir_path = Path(__file__).parent / "resources" / "example_checks"
    dir_rel_path = os.path.realpath(scan_dir_path).replace('\\', '/')

    runner_filter = RunnerFilter(framework=["kustomize"], checks=["CKV2_K8S_6"])

    mocker.patch.dict("os.environ", {"CHECKOV_GRAPH_FRAMEWORK": graph_framework})

    runner = Runner()
    runner.templateRendererCommand = "kustomize"
    runner.templateRendererCommandOptions = "build"

    report = runner.run(root_folder=dir_rel_path, runner_filter=runner_filter, external_checks_dir=None)

    summary = report.get_summary()

    assert summary["passed"] == 1
    assert summary["failed"] == 1
    assert summary["skipped"] == 1
    assert summary["parsing_errors"] == 0
