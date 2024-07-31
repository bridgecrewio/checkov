import pickle
import unittest
from pathlib import Path

from checkov.github_actions.runner import Runner
from checkov.github_actions.utils import build_gha_definitions_context
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
    definitions = {'/Users/mamelchenko/development/checkov/tests/github_actions/gha/.github/workflows/failed.yaml': {'name': 'read-only', 'on': {'pull_request': {'types': ['opened', 'synchronize', 'labeled', 'unlabeled'], '__startline__': 5, '__endline__': 7}, '__startline__': 4, '__endline__': 7}, 'permissions': 'write-all', 'jobs': {'example': {'runs-on': 'ubuntu-latest', 'steps': [{'uses': 'actions/checkout@12345678', '__startline__': 13, '__endline__': 14}, {'run': 'echo "working hard"\n', '__startline__': 14, '__endline__': 16}], '__startline__': 11, '__endline__': 16}, '__startline__': 10, '__endline__': 16}, '__startline__': 1, '__endline__': 16}}
    definitions_raw = {'/Users/mamelchenko/development/checkov/tests/github_actions/gha/.github/workflows/failed.yaml': [(1, 'name: read-only\n'), (2, '\n'), (3, 'on:\n'), (4, '  pull_request:\n'), (5, '    types: [ opened, synchronize, labeled, unlabeled ]\n'), (6, '\n'), (7, 'permissions: write-all\n'), (8, '\n'), (9, 'jobs:\n'), (10, '  example:\n'), (11, '    runs-on: ubuntu-latest\n'), (12, '    steps:\n'), (13, '      - uses: actions/checkout@12345678\n'), (14, '      - run: |\n'), (15, '          echo "working hard"\n')]}
    context = build_gha_definitions_context(definitions=definitions, definitions_raw=definitions_raw)

    graph_runner = Runner()
    graph_runner.graph_manager.get_reader_endpoint = mock_graph
    graph_runner.set_external_data(definitions=definitions, context=context, breadcrumbs=None)
    graph_runner.set_raw_definitions(definitions_raw=definitions_raw)
    # when
    report = graph_runner.run(files=file_dir, runner_filter=RunnerFilter(framework=["github_actions"], checks=checks))

    # then
    assert len(report.failed_checks) == 1, report.get_json()
    assert len(report.passed_checks) == 0, report.get_json()
    assert len(report.skipped_checks) == 0, report.get_json()
    assert len(report.parsing_errors) == 0, report.get_json()


if __name__ == "__main__":
    unittest.main()
