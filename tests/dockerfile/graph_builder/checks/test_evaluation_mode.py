import os
import warnings
from pathlib import Path
from unittest import TestCase

from parameterized import parameterized_class

from tests.graph_utils.utils import set_db_connector_by_graph_framework, PARAMETERIZED_GRAPH_FRAMEWORKS
from checkov.common.checks_infra.checks_parser import GraphCheckParser
from checkov.common.checks_infra.registry import Registry
from checkov.common.models.enums import CheckResult
from checkov.dockerfile.graph_manager import DockerfileGraphManager
from checkov.runner_filter import RunnerFilter

TEST_DIRNAME = os.path.dirname(os.path.realpath(__file__))


@parameterized_class(PARAMETERIZED_GRAPH_FRAMEWORKS)
class TestEvaluationModeAny(TestCase):
    def setUp(self) -> None:
        warnings.filterwarnings("ignore", category=ResourceWarning)
        warnings.filterwarnings("ignore", category=DeprecationWarning)

    def _run_check(self, resource_dir: str) -> dict:
        db_connector = set_db_connector_by_graph_framework(self.graph_framework)
        graph_manager = DockerfileGraphManager(db_connector=db_connector)

        checks_dir = os.path.join(TEST_DIRNAME, "evaluation_mode_checks")
        local_graph, _ = graph_manager.build_graph_from_source_directory(
            source_dir=resource_dir,
        )
        graph = graph_manager.save_graph(local_graph)
        registry = Registry(parser=GraphCheckParser(), checks_dir=checks_dir)
        registry.load_checks()
        results = registry.run_checks(graph, RunnerFilter(checks=["CKV2_DOCKER_EVAL_ANY"]), None)

        passed = []
        failed = []
        for check, check_results in results.items():
            for result in check_results:
                if result["result"] == CheckResult.PASSED:
                    passed.append(result)
                elif result["result"] == CheckResult.FAILED:
                    failed.append(result)

        return {"passed": passed, "failed": failed}

    def test_any_mode_passes_when_at_least_one_matches(self):
        """When evaluation_mode is 'any', the check should pass if at least one
        RUN instruction in the file matches the condition."""
        resource_dir = os.path.join(TEST_DIRNAME, "resources/EvaluationModeAny/pass")
        results = self._run_check(resource_dir)

        # Both RUN instructions should pass because at least one matches
        self.assertEqual(len(results["passed"]), 2)
        self.assertEqual(len(results["failed"]), 0)

    def test_any_mode_fails_when_none_match(self):
        """When evaluation_mode is 'any' and no RUN instruction matches,
        it should report one representative failure per file."""
        resource_dir = os.path.join(TEST_DIRNAME, "resources/EvaluationModeAny/fail")
        results = self._run_check(resource_dir)

        # One representative failure for the file
        self.assertEqual(len(results["passed"]), 0)
        self.assertEqual(len(results["failed"]), 1)

    def test_default_mode_evaluates_each_independently(self):
        """Without evaluation_mode (default 'all'), each RUN instruction is
        evaluated independently - one passes, one fails."""
        db_connector = set_db_connector_by_graph_framework(self.graph_framework)
        graph_manager = DockerfileGraphManager(db_connector=db_connector)

        checks_dir = os.path.join(TEST_DIRNAME, "evaluation_mode_checks")
        resource_dir = os.path.join(TEST_DIRNAME, "resources/EvaluationModeAny/pass")
        local_graph, _ = graph_manager.build_graph_from_source_directory(
            source_dir=resource_dir,
        )
        graph = graph_manager.save_graph(local_graph)
        registry = Registry(parser=GraphCheckParser(), checks_dir=checks_dir)
        registry.load_checks()
        # Use the "all" mode check
        results = registry.run_checks(graph, RunnerFilter(checks=["CKV2_DOCKER_EVAL_ALL"]), None)

        passed = []
        failed = []
        for check, check_results in results.items():
            for result in check_results:
                if result["result"] == CheckResult.PASSED:
                    passed.append(result)
                elif result["result"] == CheckResult.FAILED:
                    failed.append(result)

        # Default behavior: one passes, one fails
        self.assertEqual(len(passed), 1)
        self.assertEqual(len(failed), 1)
