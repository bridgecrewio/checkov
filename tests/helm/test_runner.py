import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock
from unittest.mock import patch
from checkov.common.bridgecrew.severities import Severities, BcSeverities
from checkov.common.models.enums import CheckResult
from checkov.common.output.record import Record
from checkov.common.output.report import CheckType, Report
from checkov.runner_filter import RunnerFilter
from checkov.helm.runner import Runner, fix_report_paths, _get_chart_remote_repos, _get_blocked_helm_repos
from tests.helm.utils import helm_exists


class TestRunnerValid(unittest.TestCase):
    @unittest.skipIf(not helm_exists(), "helm not installed")
    def test_record_relative_path_with_relative_dir(self):
        # test whether the record's repo_file_path is correct, relative to the CWD (with a / at the start).

        # this is just constructing the scan dir as normal
        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_dir_path = os.path.join(current_dir, "runner", "resources", "infrastructure")

        # this is the relative path to the directory to scan (what would actually get passed to the -d arg)
        dir_rel_path = os.path.relpath(scan_dir_path).replace("\\", "/")

        checks_allowlist = ["CKV_K8S_42"]

        runner = Runner()
        report = runner.run(
            root_folder=dir_rel_path, runner_filter=RunnerFilter(framework=["helm"], checks=checks_allowlist)
        )

        all_checks = report.failed_checks + report.passed_checks
        self.assertEqual(len(report.passed_checks), 0)
        self.assertEqual(len(report.failed_checks), 1)
        self.assertEqual(report.check_type, CheckType.HELM)
        for record in all_checks:
            self.assertIn(record.repo_file_path, record.file_path)
        for resource in report.resources:
            self.assertIn('/helm-tiller/pwnchart/templates', resource)

    @unittest.skipIf(not helm_exists(), "helm not installed")
    def test_runner_honors_enforcement_rules(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_dir_path = os.path.join(current_dir, "runner", "resources", "infrastructure")

        runner = Runner()
        filter = RunnerFilter(framework=['helm'], use_enforcement_rules=True)
        # this is not quite a true test, because the checks don't have severities. However, this shows that the check registry
        # passes the report type properly to RunnerFilter.should_run_check, and we have tests for that method
        filter.enforcement_rule_configs = {CheckType.HELM: Severities[BcSeverities.OFF]}
        report = runner.run(
            root_folder=scan_dir_path, runner_filter=filter
        )

        self.assertEqual(len(report.failed_checks), 0)
        self.assertEqual(len(report.passed_checks), 0)
        self.assertEqual(len(report.skipped_checks), 0)
        self.assertEqual(len(report.parsing_errors), 0)
        
    @unittest.skipIf(not helm_exists(), "helm not installed")
    def test_runner_invalid_chart(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_dir_path = os.path.join(current_dir, "runner", "resources", "schema-registry")

        runner = Runner()
        filter = RunnerFilter(framework=['helm'], use_enforcement_rules=False)
        # this is not quite a true test, because the checks don't have severities. However, this shows that the check registry
        # passes the report type properly to RunnerFilter.should_run_check, and we have tests for that method
        report = runner.run(
            root_folder=scan_dir_path, runner_filter=filter
        )

        self.assertEqual(len(report.failed_checks), 0)

    @unittest.skipIf(not helm_exists(), "helm not installed")
    def test_get_binary_output_from_directory_equals_to_get_binary_result(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_dir_path = os.path.join(current_dir, "runner", "resources", "schema-registry")

        runner_filter = RunnerFilter(framework=['helm'], use_enforcement_rules=False)

        chart_meta = Runner.parse_helm_chart_details(scan_dir_path)
        chart_item = (scan_dir_path, chart_meta)
        regular_result = Runner.get_binary_output(chart_item, target_dir='./tmp', helm_command="helm",
                                                  runner_filter=runner_filter)
        result_from_directory = Runner.get_binary_output_from_directory(str(scan_dir_path),
                                                                        target_dir='./tmp', helm_command="helm",
                                                                        runner_filter=runner_filter)
        assert regular_result == result_from_directory

    def test_fix_report_paths(self):
        # Create a test report with some checks
        report = Report(CheckType.HELM)
        tmp_dir = "/tmp/helm_test"
        original_root_folder = "/original/root"

        # Create template mapping
        template_mapping = {
            "/tmp/helm_test/manifest1.yaml": "/original/root/chart/templates/manifest1.yaml",
            "/tmp/helm_test/manifest2.yaml": "/original/root/chart/templates/manifest2.yaml",
            "/tmp/helm_test/unknown.yaml": "/original/root/chart/templates/unknown.yaml",
        }

        # Create some test records
        failed_check1 = Record(
            check_id="CKV_K8S_1",
            check_name="Test check 1",
            check_result={"result": CheckResult.FAILED},
            code_block=[],
            file_path=f"{tmp_dir}/manifest1.yaml",
            file_line_range=[1, 10],
            resource="resource1",
            evaluations={},
            check_class="",
            file_abs_path=f"{tmp_dir}/manifest1.yaml",
            entity_tags={},
        )

        passed_check1 = Record(
            check_id="CKV_K8S_2",
            check_name="Test check 2",
            check_result={"result": CheckResult.PASSED},
            code_block=[],
            file_path=f"{tmp_dir}/manifest2.yaml",
            file_line_range=[1, 10],
            resource="resource2",
            evaluations={},
            check_class="",
            file_abs_path=f"{tmp_dir}/manifest2.yaml",
            entity_tags={},
        )

        # Add unknown path check to test edge case
        unknown_check = Record(
            check_id="CKV_K8S_3",
            check_name="Test check 3",
            check_result={"result": CheckResult.FAILED},
            code_block=[],
            file_path=f"{tmp_dir}/unknown.yaml",
            file_line_range=[1, 10],
            resource="resource3",
            evaluations={},
            check_class="",
            file_abs_path=f"{tmp_dir}/unknown.yaml",
            entity_tags={},
        )

        report.failed_checks = [failed_check1, unknown_check]
        report.passed_checks = [passed_check1]

        # Add resources to report
        report.resources = {
            f"{tmp_dir}/manifest1.yaml:resource1",
            f"{tmp_dir}/manifest2.yaml:resource2",
            f"{tmp_dir}/unknown.yaml:resource3"
        }

        # Run the function to test
        fix_report_paths(report, tmp_dir, template_mapping, original_root_folder)

        # Check the results
        self.assertEqual(failed_check1.repo_file_path, "/chart/templates/manifest1.yaml")
        self.assertEqual(failed_check1.file_path, "/chart/templates/manifest1.yaml")
        self.assertEqual(failed_check1.file_abs_path, "/original/root/chart/templates/manifest1.yaml")

        self.assertEqual(passed_check1.repo_file_path, "/chart/templates/manifest2.yaml")
        self.assertEqual(passed_check1.file_path, "/chart/templates/manifest2.yaml")
        self.assertEqual(passed_check1.file_abs_path, "/original/root/chart/templates/manifest2.yaml")

        # Unknown path should just have the temp dir prefix removed
        self.assertEqual(unknown_check.repo_file_path, "/chart/templates/unknown.yaml")

        # Check that resources are also updated
        self.assertIn("/original/root/chart/templates/manifest1.yaml:resource1", report.resources)
        self.assertIn("/original/root/chart/templates/manifest2.yaml:resource2", report.resources)
        self.assertIn("/original/root/chart/templates/unknown.yaml:resource3", report.resources)

    def test_parse_output(self):
        # Create a temp directory for the test
        with tempfile.TemporaryDirectory() as target_dir:
            # Sample helm template output with multiple resources
            helm_output = b"---\n# Source: mychart/templates/service.yaml\napiVersion: v1\nkind: Service\nmetadata:\n  name: example-service\nspec:\n  selector:\n    app: example\n  ports:\n    - port: 80\n      targetPort: 8080\n---\n# Source: mychart/templates/deployment.yaml\napiVersion: apps/v1\nkind: Deployment\nmetadata:\n  name: example-deployment\nspec:\n  replicas: 3\n  template:\n    metadata:\n      labels:\n        app: example\n    spec:\n      containers:\n      - name: example\n        image: example:1.0"

            # Create a temporary chart directory
            with tempfile.TemporaryDirectory() as chart_dir:
                # Set up the chart directory structure
                templates_dir = os.path.join(chart_dir, "templates")
                os.makedirs(templates_dir, exist_ok=True)

                # Create template files to test mapping
                with open(os.path.join(templates_dir, "service.yaml"), 'w') as f:
                    f.write("# Original service template")

                with open(os.path.join(templates_dir, "deployment.yaml"), 'w') as f:
                    f.write("# Original deployment template")

                # Create an empty template mapping dictionary
                template_mapping = {}

                # Call the parse_output function
                Runner._parse_output(target_dir, helm_output, chart_dir, template_mapping)

                # Check template mapping was populated correctly
                expected_mapping = {
                    f'{target_dir}/mychart/templates/service.yaml': os.path.join(chart_dir, "templates/service.yaml"),
                    f'{target_dir}/mychart/templates/deployment.yaml': os.path.join(chart_dir, "templates/deployment.yaml")
                }

                # Compare the mappings - normalize paths for comparison
                normalized_template_mapping = {k.replace('\\', '/'): v.replace('\\', '/')
                                               for k, v in template_mapping.items()}
                normalized_expected_mapping = {k.replace('\\', '/'): v.replace('\\', '/')
                                               for k, v in expected_mapping.items()}

                self.assertEqual(normalized_template_mapping, normalized_expected_mapping)

                # Verify file content was written correctly
                service_file_path = os.path.join(target_dir, "mychart/templates/service.yaml")
                deployment_file_path = os.path.join(target_dir, "mychart/templates/deployment.yaml")

                if os.path.exists(service_file_path):
                    with open(service_file_path, 'r') as f:
                        content = f.read()
                        self.assertIn("kind: Service", content)
                        self.assertIn("name: example-service", content)

                if os.path.exists(deployment_file_path):
                    with open(deployment_file_path, 'r') as f:
                        content = f.read()
                        self.assertIn("kind: Deployment", content)
                        self.assertIn("name: example-deployment", content)

    @unittest.skipIf(not helm_exists(), "helm not installed")
    def test_check_system_deps(self):
        o = Runner().check_system_deps()
        assert o == None
        r = Runner()
        r.helm_command = 'thisshouldfail'
        assert r.check_system_deps() == "helm"

class TestHelmDependencyRemoteRepos(unittest.TestCase):
    """Tests for helm remote dependency repository allowlist.

    Default behaviour: helm template --dependency-update runs normally (original behaviour preserved).
    Blocking is opt-in via CHECKOV_HELM_ALLOWED_REMOTE_REPOS — an allowlist of trusted repo URL prefixes.
    Dependency repos NOT in the allowlist cause the build to be skipped.
    """

    _REMOTE_DEP_DIR = str(Path(__file__).parent / "runner/resources/example_remote_dep")

    def _make_chart_item(self) -> tuple[str, dict]:
        return (self._REMOTE_DEP_DIR, {"name": "example-chart", "version": "0.1.0"})

    # ------------------------------------------------------------------
    # _get_chart_remote_repos() unit tests
    # ------------------------------------------------------------------

    def test_get_chart_remote_repos_detects_http_url(self):
        """_get_chart_remote_repos() must return http:// dependency repos."""
        repos = _get_chart_remote_repos(self._REMOTE_DEP_DIR)
        self.assertIn("http://192.0.2.1", repos)

    def test_get_chart_remote_repos_returns_empty_for_missing_dir(self):
        """_get_chart_remote_repos() must not raise for a missing directory."""
        self.assertEqual(_get_chart_remote_repos("/nonexistent/path"), [])

    # ------------------------------------------------------------------
    # _get_blocked_helm_repos() unit tests (allowlist logic)
    # ------------------------------------------------------------------

    def test_get_blocked_helm_repos_returns_empty_when_no_env_var(self):
        """Default: no env var → _get_blocked_helm_repos() returns [] (allow all)."""
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("CHECKOV_HELM_ALLOWED_REMOTE_REPOS", None)
            repos = _get_blocked_helm_repos(self._REMOTE_DEP_DIR)
        self.assertEqual(repos, [])

    def test_get_blocked_helm_repos_returns_blocked_when_not_in_allowlist(self):
        """Repos NOT in the allowlist must be returned (they will be blocked)."""
        env = {"CHECKOV_HELM_ALLOWED_REMOTE_REPOS": "https://charts.trusted.org/"}
        with mock.patch.dict(os.environ, env):
            repos = _get_blocked_helm_repos(self._REMOTE_DEP_DIR)
        self.assertIn("http://192.0.2.1", repos)

    def test_get_blocked_helm_repos_returns_empty_when_all_in_allowlist(self):
        """When all repos are in the allowlist, nothing is blocked."""
        env = {"CHECKOV_HELM_ALLOWED_REMOTE_REPOS": "http://192.0.2.1"}
        with mock.patch.dict(os.environ, env):
            repos = _get_blocked_helm_repos(self._REMOTE_DEP_DIR)
        self.assertEqual(repos, [])

    # ------------------------------------------------------------------
    # get_binary_output() integration tests
    # ------------------------------------------------------------------

    def test_dependency_update_in_args_by_default(self):
        """Default (no env var): --dependency-update is in helm args (original behaviour)."""
        chart_item = self._make_chart_item()
        fake_output = b"apiVersion: v1\nkind: ConfigMap\n"
        mock_proc = mock.MagicMock()
        mock_proc.communicate.return_value = (fake_output, b"")
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("CHECKOV_HELM_ALLOWED_REMOTE_REPOS", None)
            with mock.patch("subprocess.Popen", return_value=mock_proc) as mock_popen:
                Runner.get_binary_output(chart_item, "./tmp", "helm", RunnerFilter())
        call_args = mock_popen.call_args[0][0]
        self.assertIn("--dependency-update", call_args)

    def test_build_skipped_when_repo_not_in_allowlist(self):
        """When CHECKOV_HELM_ALLOWED_REMOTE_REPOS is set and a repo is not in it, build is skipped."""
        chart_item = self._make_chart_item()
        # The first subprocess.Popen call is 'helm dependency list' (before the allowlist check).
        # We must mock it so it does not crash; the allowlist check then returns None before the second call.
        dep_list_proc = mock.MagicMock()
        dep_list_proc.communicate.return_value = (b"", b"")
        env = {"CHECKOV_HELM_ALLOWED_REMOTE_REPOS": "https://charts.trusted.org/"}
        with mock.patch.dict(os.environ, env):
            with mock.patch("subprocess.Popen", return_value=dep_list_proc) as mock_popen:
                result, _ = Runner.get_binary_output(chart_item, "./tmp", "helm", RunnerFilter())
        self.assertIsNone(result)
        # Only the dependency list call should have been made; helm template must NOT be called.
        self.assertEqual(mock_popen.call_count, 1)
        self.assertIn("dependency", mock_popen.call_args[0][0])

    def test_build_proceeds_when_all_repos_in_allowlist(self):
        """When all repos are in the allowlist, build proceeds normally."""
        chart_item = self._make_chart_item()
        fake_output = b"apiVersion: v1\nkind: ConfigMap\n"
        dep_list_proc = mock.MagicMock()
        dep_list_proc.communicate.return_value = (b"", b"")
        template_proc = mock.MagicMock()
        template_proc.communicate.return_value = (fake_output, b"")
        env = {"CHECKOV_HELM_ALLOWED_REMOTE_REPOS": "http://192.0.2.1"}
        with mock.patch.dict(os.environ, env):
            with mock.patch("subprocess.Popen", side_effect=[dep_list_proc, template_proc]) as mock_popen:
                result, _ = Runner.get_binary_output(chart_item, "./tmp", "helm", RunnerFilter())
        self.assertEqual(mock_popen.call_count, 2)
        self.assertEqual(result, fake_output)

    def test_chart_dir_always_last_arg(self):
        """chart_dir must always be the last argument."""
        chart_item = self._make_chart_item()
        fake_output = b"apiVersion: v1\nkind: ConfigMap\n"
        mock_proc = mock.MagicMock()
        mock_proc.communicate.return_value = (fake_output, b"")
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("CHECKOV_HELM_ALLOWED_REMOTE_REPOS", None)
            with mock.patch("subprocess.Popen", return_value=mock_proc) as mock_popen:
                Runner.get_binary_output(chart_item, "./tmp", "helm", RunnerFilter())
        call_args = mock_popen.call_args[0][0]
        self.assertEqual(call_args[-1], self._REMOTE_DEP_DIR)


if __name__ == "__main__":
    unittest.main()
