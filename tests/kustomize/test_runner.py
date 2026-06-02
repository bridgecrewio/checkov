import os
import unittest
from pathlib import Path
from unittest import mock

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.bridgecrew.severities import Severities, BcSeverities
from checkov.runner_filter import RunnerFilter
from checkov.kustomize.runner import Runner, _has_remote_refs
from tests.kustomize.utils import kustomize_exists


def _setup_test_under_example():
    current_dir = os.path.dirname(os.path.realpath(__file__))
    scan_dir_path = os.path.join(current_dir, "runner", "resources", "example")
    # this is the relative path to the directory to scan (what would actually get passed to the -d arg)
    dir_rel_path = os.path.relpath(scan_dir_path).replace('\\', '/')
    runner = Runner()
    runner.templateRendererCommand = "kustomize"
    runner.templateRendererCommandOptions = "build"
    checks_allowlist = ['CKV_K8S_37']
    return checks_allowlist, dir_rel_path, runner


class TestRunnerValid(unittest.TestCase):
    @unittest.skipIf(os.name == "nt" or not kustomize_exists(), "kustomize not installed or Windows OS")
    def test_runner_honors_enforcement_rules(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_dir_path = os.path.join(current_dir, "runner", "resources", "example")

        # this is the relative path to the directory to scan (what would actually get passed to the -d arg)
        dir_rel_path = os.path.relpath(scan_dir_path).replace('\\', '/')

        runner = Runner()
        runner.templateRendererCommand = "kustomize"
        runner.templateRendererCommandOptions = "build"
        filter = RunnerFilter(framework=['kustomize'], use_enforcement_rules=True)
        # this is not quite a true test, because the checks don't have severities. However, this shows that the check registry
        # passes the report type properly to RunnerFilter.should_run_check, and we have tests for that method
        filter.enforcement_rule_configs = {CheckType.KUSTOMIZE: Severities[BcSeverities.OFF]}
        report = runner.run(root_folder=dir_rel_path, external_checks_dir=None,
                            runner_filter=filter)

        self.assertEqual(len(report.failed_checks), 0)
        self.assertEqual(len(report.passed_checks), 0)
        self.assertEqual(len(report.skipped_checks), 0)
        self.assertEqual(len(report.parsing_errors), 0)

    @unittest.skipIf(os.name == "nt" or not kustomize_exists(), "kustomize not installed or Windows OS")
    def test_record_relative_path_with_relative_dir(self):
        # test whether the record's repo_file_path is correct, relative to the CWD (with a / at the start).

        # this is just constructing the scan dir as normal
        checks_allowlist, dir_rel_path, runner = _setup_test_under_example()
        report = runner.run(root_folder=dir_rel_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework=['kustomize'], checks=checks_allowlist))

        all_checks = report.failed_checks + report.passed_checks
        self.assertGreater(len(all_checks), 0)  # ensure that the assertions below are going to do something
        for record in all_checks:
            self.assertIn(record.file_path, record.file_abs_path)
            self.assertEqual(record.repo_file_path, f'/{dir_rel_path}{record.file_path}')
            assert record.file_path.startswith(('/base', '/overlays'))

    @unittest.skipIf(os.name == "nt" or not kustomize_exists(), "kustomize not installed or Windows OS")
    def test_record_relative_path_with_relative_dir_with_origin_annotations(self):
        # test whether the record's repo_file_path is correct, relative to the CWD (with a / at the start).

        # this is just constructing the scan dir as normal
        with mock.patch.dict(os.environ, {"CHECKOV_ALLOW_KUSTOMIZE_FILE_EDITS": "True"}):
            checks_allowlist, dir_rel_path, runner = _setup_test_under_example()
            report = runner.run(root_folder=dir_rel_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework=['kustomize'], checks=checks_allowlist))

        all_checks = report.failed_checks + report.passed_checks
        self.assertGreater(len(all_checks), 0)  # ensure that the assertions below are going to do something
        for record in all_checks:
            self.assertIn(record.file_path, record.file_abs_path)
            self.assertEqual(record.repo_file_path, f'/{dir_rel_path}{record.file_path}')
            assert record.file_path.startswith(('/base', '/overlays'))
            assert record.caller_file_path == '/base/deployment.yaml' or record.caller_file_path == '/deployment.yaml'
            assert record.caller_file_line_range == (2, 24)

    @unittest.skipIf(os.name == "nt" or not kustomize_exists(), "kustomize not installed or Windows OS")
    def test_record_relative_path_with_direct_oberlay(self):
        # test whether the record's repo_file_path is correct, relative to the CWD (with a / at the start).

        # this is just constructing the scan dir as normal
        scan_dir_path = Path(__file__).parent / "runner/resources/example/overlays/dev"


        # this is the relative path to the directory to scan (what would actually get passed to the -d arg)
        dir_rel_path = os.path.relpath(scan_dir_path).replace('\\', '/')

        runner = Runner()
        runner.templateRendererCommand = "kustomize"
        runner.templateRendererCommandOptions = "build"
        checks_allowlist = ['CKV_K8S_37']
        report = runner.run(root_folder=dir_rel_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework=['kustomize'], checks=checks_allowlist))

        all_checks = report.failed_checks + report.passed_checks
        self.assertGreater(len(all_checks), 0)  # ensure that the assertions below are going to do something
        for record in all_checks:
            self.assertNotEqual(record.file_path, record.file_abs_path)
            self.assertIn(record.file_path, record.file_abs_path)
            self.assertEqual(record.repo_file_path, f'/{dir_rel_path}{record.file_path}')

    @unittest.skipIf(os.name == "nt" or not kustomize_exists(), "kustomize not installed or Windows OS")
    def test_record_relative_path_with_direct_prod2_oberlay(self):
        # test whether the record's repo_file_path is correct, relative to the CWD (with a / at the start).

        # this is just constructing the scan dir as normal
        scan_dir_path = Path(__file__).parent / "runner/resources/example/overlays/prod-2"


        # this is the relative path to the directory to scan (what would actually get passed to the -d arg)
        dir_rel_path = os.path.relpath(scan_dir_path).replace('\\', '/')

        runner = Runner()
        runner.templateRendererCommand = "kustomize"
        runner.templateRendererCommandOptions = "build"
        checks_allowlist = ['CKV_K8S_37']
        report = runner.run(root_folder=dir_rel_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework=['kustomize'], checks=checks_allowlist))

        all_checks = report.failed_checks + report.passed_checks
        self.assertGreater(len(all_checks), 0)  # ensure that the assertions below are going to do something
        for record in all_checks:
            self.assertNotEqual(record.file_path, record.file_abs_path)
            self.assertIn(record.file_path, record.file_abs_path)
            self.assertEqual(record.repo_file_path, f'/{dir_rel_path}{record.file_path}')

    
    @unittest.skipIf(os.name == "nt" or not kustomize_exists(), "kustomize not installed or Windows OS")
    def test_no_file_type_exists(self):
        # test whether the record's repo_file_path is correct, relative to the CWD (with a / at the start).

        # this is just constructing the scan dir as normal
        scan_dir_path = Path(__file__).parent / "runner/resources/example/no_type"


        # this is the relative path to the directory to scan (what would actually get passed to the -d arg)
        dir_rel_path = os.path.relpath(scan_dir_path).replace('\\', '/')

        runner = Runner()
        runner.templateRendererCommand = "kustomize"
        runner.templateRendererCommandOptions = "build"
        report = runner.run(root_folder=dir_rel_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework=['kustomize']))

        all_checks = report.failed_checks + report.passed_checks
        self.assertEqual(len(all_checks), 0)  # we should no get any results

    @unittest.skipIf(os.name == "nt" or not kustomize_exists(), "kustomize not installed or Windows OS")
    def test_get_binary_output_from_directory_equals_to_get_binary_result(self):
        scan_dir_path = Path(__file__).parent / "runner/resources/example/no_type"
        dir_rel_path = os.path.relpath(scan_dir_path).replace('\\', '/')
        runner = Runner()
        runner.templateRendererCommand = "kustomize"
        runner.templateRendererCommandOptions = "build"

        # Runs the runner fully just to build `runner.kustomizeProcessedFolderAndMeta`
        _ = runner.run(root_folder=dir_rel_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework=['kustomize']))
        regular_result = runner.get_binary_output(str(scan_dir_path), runner.kustomizeProcessedFolderAndMeta,
                                                  runner.templateRendererCommand)
        result_from_directory = runner.get_binary_output_from_directory(str(scan_dir_path),
                                                                        runner.templateRendererCommand)
        assert regular_result == result_from_directory



class TestRemoteBaseSSRF(unittest.TestCase):
    """Tests for F-11: Kustomize Remote Base SSRF (CWE-918)."""

    _REMOTE_BASE_DIR = str(Path(__file__).parent / "runner/resources/example_remote_base")

    # ------------------------------------------------------------------
    # Unit tests for the helper function (no kustomize binary needed)
    # ------------------------------------------------------------------

    def test_has_remote_refs_detects_http_url(self):
        """_has_remote_refs() must flag http:// entries in resources:."""
        refs = _has_remote_refs(self._REMOTE_BASE_DIR)
        self.assertIn("http://169.254.169.254/latest/meta-data/", refs)

    def test_has_remote_refs_detects_git_url(self):
        """_has_remote_refs() must flag git:: entries in resources:."""
        refs = _has_remote_refs(self._REMOTE_BASE_DIR)
        self.assertTrue(any(r.startswith("git::") for r in refs),
                        f"Expected a git:: ref in {refs}")

    def test_has_remote_refs_returns_empty_for_local_only(self):
        """_has_remote_refs() must return [] for a kustomization with only local refs."""
        local_dir = str(Path(__file__).parent / "runner/resources/example/base")
        refs = _has_remote_refs(local_dir)
        self.assertEqual(refs, [])

    def test_has_remote_refs_returns_empty_for_missing_dir(self):
        """_has_remote_refs() must not raise for a directory without a kustomization file."""
        refs = _has_remote_refs("/nonexistent/path/that/does/not/exist")
        self.assertEqual(refs, [])

    # ------------------------------------------------------------------
    # Integration tests: _get_kubectl_output() must skip remote bases
    # (no real network call is made because we mock subprocess.Popen)
    # ------------------------------------------------------------------

    def _make_runner(self) -> Runner:
        runner = Runner()
        runner.templateRendererCommand = "kustomize"
        return runner

    def test_get_kubectl_output_blocks_remote_refs_by_default(self):
        """_get_kubectl_output() must return None when remote refs are present and
        CHECKOV_KUSTOMIZE_ALLOW_REMOTE is not set (default safe behaviour)."""
        runner = self._make_runner()
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("CHECKOV_KUSTOMIZE_ALLOW_REMOTE", None)
            with mock.patch("subprocess.Popen") as mock_popen:
                result = runner._get_kubectl_output(
                    self._REMOTE_BASE_DIR, "kustomize", "base"
                )
        self.assertIsNone(result, "Expected None when remote refs are present")
        mock_popen.assert_not_called()

    def test_get_kubectl_output_blocks_remote_refs_when_env_false(self):
        """_get_kubectl_output() must return None when CHECKOV_KUSTOMIZE_ALLOW_REMOTE=false."""
        runner = self._make_runner()
        with mock.patch.dict(os.environ, {"CHECKOV_KUSTOMIZE_ALLOW_REMOTE": "false"}):
            with mock.patch("subprocess.Popen") as mock_popen:
                result = runner._get_kubectl_output(
                    self._REMOTE_BASE_DIR, "kustomize", "base"
                )
        self.assertIsNone(result)
        mock_popen.assert_not_called()

    def test_get_kubectl_output_allows_remote_refs_when_env_true(self):
        """_get_kubectl_output() must invoke kustomize when CHECKOV_KUSTOMIZE_ALLOW_REMOTE=true."""
        runner = self._make_runner()
        fake_output = b"apiVersion: v1\nkind: ConfigMap\n"
        mock_proc = mock.MagicMock()
        mock_proc.communicate.return_value = (fake_output, b"")
        with mock.patch.dict(os.environ, {"CHECKOV_KUSTOMIZE_ALLOW_REMOTE": "true"}):
            with mock.patch("subprocess.Popen", return_value=mock_proc) as mock_popen:
                result = runner._get_kubectl_output(
                    self._REMOTE_BASE_DIR, "kustomize", "base"
                )
        mock_popen.assert_called_once()
        self.assertEqual(result, fake_output)

    def test_get_kubectl_output_allows_local_refs_without_env(self):
        """_get_kubectl_output() must invoke kustomize for local-only kustomizations."""
        runner = self._make_runner()
        local_dir = str(Path(__file__).parent / "runner/resources/example/base")
        fake_output = b"apiVersion: v1\nkind: ConfigMap\n"
        mock_proc = mock.MagicMock()
        mock_proc.communicate.return_value = (fake_output, b"")
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("CHECKOV_KUSTOMIZE_ALLOW_REMOTE", None)
            with mock.patch("subprocess.Popen", return_value=mock_proc) as mock_popen:
                result = runner._get_kubectl_output(local_dir, "kustomize", "base")
        mock_popen.assert_called_once()
        self.assertEqual(result, fake_output)

    # ------------------------------------------------------------------
    # Prefix allowlist tests (CHECKOV_KUSTOMIZE_ALLOWED_REMOTE_PREFIXES)
    # ------------------------------------------------------------------

    def test_allowed_prefix_permits_matching_url(self):
        """A remote ref matching an allowed prefix must not block the build."""
        runner = self._make_runner()
        fake_output = b"apiVersion: v1\nkind: ConfigMap\n"
        mock_proc = mock.MagicMock()
        mock_proc.communicate.return_value = (fake_output, b"")
        # The fixture contains http://169.254.169.254/... — allow that prefix
        env = {"CHECKOV_KUSTOMIZE_ALLOWED_REMOTE_PREFIXES": "http://169.254.169.254/,git::https://attacker.example/"}
        with mock.patch.dict(os.environ, env):
            os.environ.pop("CHECKOV_KUSTOMIZE_ALLOW_REMOTE", None)
            with mock.patch("subprocess.Popen", return_value=mock_proc) as mock_popen:
                result = runner._get_kubectl_output(self._REMOTE_BASE_DIR, "kustomize", "base")
        mock_popen.assert_called_once()
        self.assertEqual(result, fake_output)

    def test_allowed_prefix_blocks_non_matching_url(self):
        """A remote ref NOT matching any allowed prefix must still block the build."""
        runner = self._make_runner()
        # Allow only a trusted org — the fixture's attacker URL must still be blocked
        env = {"CHECKOV_KUSTOMIZE_ALLOWED_REMOTE_PREFIXES": "https://github.com/trusted-org/"}
        with mock.patch.dict(os.environ, env):
            os.environ.pop("CHECKOV_KUSTOMIZE_ALLOW_REMOTE", None)
            with mock.patch("subprocess.Popen") as mock_popen:
                result = runner._get_kubectl_output(self._REMOTE_BASE_DIR, "kustomize", "base")
        self.assertIsNone(result)
        mock_popen.assert_not_called()

    def test_allowed_prefix_partial_match_blocks_unmatched(self):
        """Only the matching refs are allowed; if any ref is unmatched the build is blocked."""
        runner = self._make_runner()
        # Allow the http:// ref but NOT the git:: ref — build must still be blocked
        env = {"CHECKOV_KUSTOMIZE_ALLOWED_REMOTE_PREFIXES": "http://169.254.169.254/"}
        with mock.patch.dict(os.environ, env):
            os.environ.pop("CHECKOV_KUSTOMIZE_ALLOW_REMOTE", None)
            with mock.patch("subprocess.Popen") as mock_popen:
                result = runner._get_kubectl_output(self._REMOTE_BASE_DIR, "kustomize", "base")
        self.assertIsNone(result)
        mock_popen.assert_not_called()


if __name__ == '__main__':
    unittest.main()
