import pickle
import unittest
from pathlib import Path

from checkov.github_actions.runner import Runner
from checkov.github_actions.utils import get_gha_files_definitions, build_gha_definitions_context
from checkov.runner_filter import RunnerFilter


def test_runner_with_existing_graph():

    def mock_graph():
        with open(str(Path(__file__).parent / 'resources/graph.pkl'), 'rb') as inp:
            graph = pickle.load(inp)
            return graph

    # given
    file_path = Path(__file__).parent / "gha/.github/workflows/failed.yaml"
    file_dir = [str(file_path)]
    checks = ["CKV2_GHA_1"]
    definitions, definitions_raw = get_gha_files_definitions(root_folder=str(Path(__file__).parent / "gha"),
                                                             files=[str(Path(__file__).parent / "gha/.github/workflows/failed.yaml")])
    context = build_gha_definitions_context(definitions=definitions, definitions_raw=definitions_raw)

    graph_runner = Runner()
    graph_runner.graph_manager.get_reader_endpoint = mock_graph
    graph_runner.set_external_data(definitions=definitions, context=context, breadcrumbs=None)
    graph_runner.set_raw_definitions(definitions_raw=definitions_raw)
    # when
    report = graph_runner.run(files=file_dir, runner_filter=RunnerFilter(framework=["github_actions"], checks=checks))

    # then
    assert len(report.failed_checks) == 1
    assert len(report.passed_checks) == 0
    assert len(report.skipped_checks) == 0
    assert len(report.parsing_errors) == 0


if __name__ == "__main__":
    unittest.main()
