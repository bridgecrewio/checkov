import os
import unittest
from pathlib import Path
from unittest import mock

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.bridgecrew.severities import Severities, BcSeverities
from checkov.runner_filter import RunnerFilter
from checkov.kustomize.runner import Runner, _get_blocked_remote_refs, _get_kustomization_remote_refs
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



class TestRemoteBaseAllowlist(unittest.TestCase):
    """Tests for kustomize remote base allowlist.

    Default behaviour: kustomize runs normally (original behaviour preserved).
    Blocking is opt-in via CHECKOV_KUSTOMIZE_ALLOWED_REMOTE_PREFIXES — an allowlist of
    trusted URL prefixes. Remote refs NOT in the allowlist are blocked.
    """

    _REMOTE_BASE_DIR = str(Path(__file__).parent / "runner/resources/example_remote_base")

    def _make_runner(self) -> Runner:
        runner = Runner()
        runner.templateRendererCommand = "kustomize"
        return runner

    # ------------------------------------------------------------------
    # _get_kustomization_remote_refs() unit tests
    # ------------------------------------------------------------------

    def test_get_kustomization_remote_refs_detects_http_url(self):
        """_get_kustomization_remote_refs() must return http:// entries."""
        refs = _get_kustomization_remote_refs(self._REMOTE_BASE_DIR)
        self.assertIn("http://192.0.2.1/example-base.yaml", refs)

    def test_get_kustomization_remote_refs_detects_git_url(self):
        """_get_kustomization_remote_refs() must return git:: entries."""
        refs = _get_kustomization_remote_refs(self._REMOTE_BASE_DIR)
        self.assertTrue(any(r.startswith("git::") for r in refs))

    def test_get_kustomization_remote_refs_returns_empty_for_local_only(self):
        """_get_kustomization_remote_refs() must return [] for local-only kustomizations."""
        local_dir = str(Path(__file__).parent / "runner/resources/example/base")
        self.assertEqual(_get_kustomization_remote_refs(local_dir), [])

    def test_get_kustomization_remote_refs_returns_empty_for_missing_dir(self):
        """_get_kustomization_remote_refs() must not raise for a missing directory."""
        self.assertEqual(_get_kustomization_remote_refs("/nonexistent/path"), [])

    # ------------------------------------------------------------------
    # _get_blocked_remote_refs() unit tests (allowlist logic)
    # ------------------------------------------------------------------

    def test_get_blocked_remote_refs_returns_empty_when_no_env_var(self):
        """Default: no env var → _get_blocked_remote_refs() returns [] (allow all)."""
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("CHECKOV_KUSTOMIZE_ALLOWED_REMOTE_PREFIXES", None)
            refs = _get_blocked_remote_refs(self._REMOTE_BASE_DIR)
        self.assertEqual(refs, [])

    def test_get_blocked_remote_refs_returns_blocked_when_not_in_allowlist(self):
        """Remote refs NOT in the allowlist must be returned (they will be blocked)."""
        env = {"CHECKOV_KUSTOMIZE_ALLOWED_REMOTE_PREFIXES": "https://github.com/trusted-org/"}
        with mock.patch.dict(os.environ, env):
            refs = _get_blocked_remote_refs(self._REMOTE_BASE_DIR)
        self.assertIn("http://192.0.2.1/example-base.yaml", refs)

    def test_get_blocked_remote_refs_returns_empty_when_all_in_allowlist(self):
        """When all remote refs are in the allowlist, nothing is blocked."""
        env = {"CHECKOV_KUSTOMIZE_ALLOWED_REMOTE_PREFIXES": "http://192.0.2.1/,git::https://example.com/"}
        with mock.patch.dict(os.environ, env):
            refs = _get_blocked_remote_refs(self._REMOTE_BASE_DIR)
        self.assertEqual(refs, [])

    def test_get_blocked_remote_refs_returns_empty_for_local_only(self):
        """Local-only kustomizations are never blocked."""
        local_dir = str(Path(__file__).parent / "runner/resources/example/base")
        env = {"CHECKOV_KUSTOMIZE_ALLOWED_REMOTE_PREFIXES": "https://github.com/trusted-org/"}
        with mock.patch.dict(os.environ, env):
            refs = _get_blocked_remote_refs(local_dir)
        self.assertEqual(refs, [])

    # ------------------------------------------------------------------
    # _get_kubectl_output() integration tests
    # ------------------------------------------------------------------

    def test_get_kubectl_output_allows_remote_refs_by_default(self):
        """Default (no env var): kustomize build runs even with remote refs."""
        runner = self._make_runner()
        fake_output = b"apiVersion: v1\nkind: ConfigMap\n"
        mock_proc = mock.MagicMock()
        mock_proc.communicate.return_value = (fake_output, b"")
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("CHECKOV_KUSTOMIZE_ALLOWED_REMOTE_PREFIXES", None)
            with mock.patch("checkov.kustomize.runner.subprocess.Popen", return_value=mock_proc) as mock_popen:
                result = runner._get_kubectl_output(self._REMOTE_BASE_DIR, "kustomize", "base")
        mock_popen.assert_called_once()
        self.assertEqual(result, fake_output)

    def test_get_kubectl_output_blocks_when_not_in_allowlist(self):
        """When CHECKOV_KUSTOMIZE_ALLOWED_REMOTE_PREFIXES is set and a ref is not in it, build is skipped."""
        runner = self._make_runner()
        env = {"CHECKOV_KUSTOMIZE_ALLOWED_REMOTE_PREFIXES": "https://github.com/trusted-org/"}
        with mock.patch.dict(os.environ, env):
            with mock.patch("checkov.kustomize.runner.subprocess.Popen") as mock_popen:
                result = runner._get_kubectl_output(self._REMOTE_BASE_DIR, "kustomize", "base")
        self.assertIsNone(result)
        mock_popen.assert_not_called()

    def test_get_kubectl_output_allows_when_all_in_allowlist(self):
        """When all remote refs are in the allowlist, build proceeds normally."""
        runner = self._make_runner()
        fake_output = b"apiVersion: v1\nkind: ConfigMap\n"
        mock_proc = mock.MagicMock()
        mock_proc.communicate.return_value = (fake_output, b"")
        env = {"CHECKOV_KUSTOMIZE_ALLOWED_REMOTE_PREFIXES": "http://192.0.2.1/,git::https://example.com/"}
        with mock.patch.dict(os.environ, env):
            with mock.patch("checkov.kustomize.runner.subprocess.Popen", return_value=mock_proc) as mock_popen:
                result = runner._get_kubectl_output(self._REMOTE_BASE_DIR, "kustomize", "base")
        mock_popen.assert_called_once()
        self.assertEqual(result, fake_output)

    def test_get_kubectl_output_allows_local_refs_without_env(self):
        """Local-only kustomizations always run regardless of env var."""
        runner = self._make_runner()
        local_dir = str(Path(__file__).parent / "runner/resources/example/base")
        fake_output = b"apiVersion: v1\nkind: ConfigMap\n"
        mock_proc = mock.MagicMock()
        mock_proc.communicate.return_value = (fake_output, b"")
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("CHECKOV_KUSTOMIZE_ALLOWED_REMOTE_PREFIXES", None)
            with mock.patch("checkov.kustomize.runner.subprocess.Popen", return_value=mock_proc) as mock_popen:
                result = runner._get_kubectl_output(local_dir, "kustomize", "base")
        mock_popen.assert_called_once()
        self.assertEqual(result, fake_output)


if __name__ == '__main__':
    unittest.main()
