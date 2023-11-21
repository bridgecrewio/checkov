import os
import unittest

from parameterized import parameterized_class

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.bridgecrew.severities import Severities, BcSeverities
from checkov.common.graph.db_connectors.networkx.networkx_db_connector import NetworkxConnector
from checkov.common.graph.db_connectors.rustworkx.rustworkx_db_connector import RustworkxConnector
from checkov.json_doc.runner import Runner
from checkov.runner_filter import RunnerFilter
from checkov.json_doc.registry import registry

@parameterized_class([
   {"db_connector": NetworkxConnector},
   {"db_connector": RustworkxConnector}
])
class TestRunnerValid(unittest.TestCase):

    def test_registry_has_type(self):
        self.assertEqual(registry.report_type, CheckType.JSON)

    def test_runner_object_failing_check(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = os.path.join(current_dir, "resources", "object", "fail")
        checks_dir = os.path.join(current_dir, "checks", "object")
        runner = Runner(db_connector=self.db_connector())
        checks = ["CKV_FOO_1", "CKV_FOO_2"]
        report = runner.run(
            root_folder=valid_dir_path,
            external_checks_dir=[checks_dir],
            runner_filter=RunnerFilter(framework='all', checks=checks)
        )
        self.assertEqual(len(report.failed_checks), 3)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(len(report.passed_checks), 2)
        self.assertEqual(report.skipped_checks, [])
        report.print_console()

    def test_runner_honors_enforcement_rules(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = os.path.join(current_dir, "resources", "object", "fail")
        checks_dir = os.path.join(current_dir, "checks", "object")
        runner = Runner(db_connector=self.db_connector())
        filter = RunnerFilter(framework=['json'], use_enforcement_rules=True)
        # this is not quite a true test, because the checks don't have severities. However, this shows that the check registry
        # passes the report type properly to RunnerFilter.should_run_check, and we have tests for that method
        filter.enforcement_rule_configs = {CheckType.JSON: Severities[BcSeverities.OFF]}
        report = runner.run(
            root_folder=valid_dir_path,
            external_checks_dir=[checks_dir],
            runner_filter=filter
        )
        self.assertEqual(len(report.failed_checks), 0)
        self.assertEqual(len(report.parsing_errors), 0)
        self.assertEqual(len(report.passed_checks), 0)
        self.assertEqual(len(report.skipped_checks), 0)
        report.print_console()

    def test_runner_object_passing_check(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = os.path.join(current_dir, "resources", "object", "pass")
        checks_dir = os.path.join(current_dir, "checks", "object")
        runner = Runner(db_connector=self.db_connector())
        report = runner.run(
            root_folder=valid_dir_path,
            external_checks_dir=[checks_dir],
            runner_filter=RunnerFilter(framework="all", checks=["CKV_FOO_1"]),
        )
        self.assertEqual(len(report.passed_checks), 1)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(report.failed_checks, [])
        self.assertEqual(report.skipped_checks, [])
        report.print_console()

    def test_runner_array_failing_check(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = os.path.join(current_dir, "resources", "array", "fail")
        checks_dir = os.path.join(current_dir, "checks", "array")
        runner = Runner(db_connector=self.db_connector())
        report = runner.run(
            root_folder=valid_dir_path,
            external_checks_dir=[checks_dir],
            runner_filter=RunnerFilter(framework='all', checks=["CKV_BARBAZ_1"])
        )
        self.assertEqual(len(report.failed_checks), 3)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(len(report.passed_checks), 1)
        self.assertEqual(report.skipped_checks, [])
        report.print_console()

    def test_runner_array_passing_check(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = os.path.join(current_dir, "resources", "array", "pass")
        checks_dir = os.path.join(current_dir, "checks", "array")
        runner = Runner(db_connector=self.db_connector())
        report = runner.run(
            root_folder=valid_dir_path,
            external_checks_dir=[checks_dir],
            runner_filter=RunnerFilter(framework="all", checks=["CKV_BARBAZ_1"]),
        )
        self.assertEqual(len(report.passed_checks), 2)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(report.failed_checks, [])
        self.assertEqual(report.skipped_checks, [])
        report.print_console()

    def test_runner_complex_failing_check(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = os.path.join(current_dir, "resources", "complex", "fail")
        checks_dir = os.path.join(current_dir, "checks", "complex")
        runner = Runner(db_connector=self.db_connector())
        report = runner.run(
            root_folder=valid_dir_path,
            external_checks_dir=[checks_dir],
            runner_filter=RunnerFilter(framework='all', checks=["CKV_COMPLEX_1"])
        )
        self.assertEqual(len(report.failed_checks), 1)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(report.passed_checks, [])
        self.assertEqual(report.skipped_checks, [])
        report.print_console()

    def test_runner_complex_passing_check(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = os.path.join(current_dir, "resources", "complex", "pass")
        checks_dir = os.path.join(current_dir, "checks", "complex")
        runner = Runner(db_connector=self.db_connector())
        report = runner.run(
            root_folder=valid_dir_path,
            external_checks_dir=[checks_dir],
            runner_filter=RunnerFilter(framework="all", checks=["CKV_COMPLEX_1"]),
        )
        self.assertEqual(len(report.passed_checks), 1)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(report.failed_checks, [])
        self.assertEqual(report.skipped_checks, [])
        report.print_console()

    def test_focused_result_configuration_no_evaluated_key(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = os.path.join(current_dir, "resources", "result_config")
        checks_dir = os.path.join(current_dir, "checks", "result_config")
        runner = Runner(db_connector=self.db_connector())
        report = runner.run(
            root_folder=valid_dir_path,
            external_checks_dir=[checks_dir],
            runner_filter=RunnerFilter(framework="all", checks=["CKV_RESULT_CONFIG_1"]),
        )
        self.assertEqual(len(report.passed_checks), 1)

        # file_line_range should cover the entire file range for empty evaluated_key path
        self.assertEqual(report.passed_checks[0].file_line_range, [1, 81])
        report.print_console()

    def test_focused_result_configuration_full_evaluated(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = os.path.join(current_dir, "resources", "result_config")
        checks_dir = os.path.join(current_dir, "checks", "result_config")
        runner = Runner(db_connector=self.db_connector())
        report = runner.run(
            root_folder=valid_dir_path,
            external_checks_dir=[checks_dir],
            runner_filter=RunnerFilter(framework="all", checks=["CKV_RESULT_CONFIG_2"]),
        )
        self.assertEqual(len(report.passed_checks), 1)

        # file_line_range should cover the object that the evaluated_key path points at
        self.assertEqual(report.passed_checks[0].file_line_range, [19, 24])
        report.print_console()

    def test_focused_result_configuration_partial_evaluated_key(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = os.path.join(current_dir, "resources", "result_config")
        checks_dir = os.path.join(current_dir, "checks", "result_config")
        runner = Runner(db_connector=self.db_connector())
        report = runner.run(
            root_folder=valid_dir_path,
            external_checks_dir=[checks_dir],
            runner_filter=RunnerFilter(framework="all", checks=["CKV_RESULT_CONFIG_3"]),
        )
        self.assertEqual(len(report.passed_checks), 1)

        # file_line_range should cover the parent object of the key that the evaluated_key path points at
        self.assertEqual(report.passed_checks[0].file_line_range, [17, 31])
        report.print_console()

    def test_get_result_configuration_for_list_type(self):
        entity_conf = [{'file_name': 'branch_protection_rules', 'org_complementary_metadata': {}, 'repo_complementary_metadata': {}}]
        evaluated_keys = ['data/organization/ipAllowListForInstalledAppsEnabledSetting']
        result_config = registry.get_result_configuration(evaluated_keys, entity_conf)
        self.assertEqual(result_config, entity_conf)

    def test_get_result_configuration_for_dict_type(self):
        entity_conf = {'required_pull_request_reviews': {'dismiss_stale_reviews': False}, 'CKV_METADATA': {'file_name': 'pass', 'org_complementary_metadata': {}, 'repo_complementary_metadata': {}}}
        evaluated_keys = ['required_pull_request_reviews/dismiss_stale_reviews']
        result_config = registry.get_result_configuration(evaluated_keys, entity_conf)
        self.assertEqual(result_config, {'dismiss_stale_reviews': False})





if __name__ == "__main__":
    unittest.main()
