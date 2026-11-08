from __future__ import annotations

from pathlib import Path
from unittest import mock

import pytest

from checkov.common.bridgecrew.check_type import CheckType
from checkov.kustomize import runner as kustomize_runner
from checkov.main import Checkov

KustomizeCommandError = getattr(kustomize_runner, "KustomizeCommandError", RuntimeError)
Runner = kustomize_runner.Runner


def test_auto_prefers_kubectl_when_both_tools_exist() -> None:
    runner = Runner()

    with mock.patch("checkov.kustomize.runner.shutil.which", side_effect=lambda command: f"/fake/{command}"), \
            mock.patch("checkov.kustomize.runner.get_kubectl_version", return_value=1.30), \
            mock.patch("checkov.kustomize.runner.get_kustomize_version") as get_kustomize_version:
        result = runner.check_system_deps()

    assert result is None
    assert runner.templateRendererCommand == "kubectl"
    get_kustomize_version.assert_not_called()


def test_auto_uses_kustomize_when_kubectl_is_absent() -> None:
    runner = Runner()

    with mock.patch(
        "checkov.kustomize.runner.shutil.which",
        side_effect=lambda command: None if command == "kubectl" else "/fake/kustomize",
    ), mock.patch("checkov.kustomize.runner.get_kustomize_version", return_value="v5.4.2"):
        result = runner.check_system_deps()

    assert result is None
    assert runner.templateRendererCommand == "kustomize"


def test_auto_disables_runner_when_neither_tool_exists() -> None:
    runner = Runner()

    with mock.patch("checkov.kustomize.runner.shutil.which", return_value=None):
        result = runner.check_system_deps()

    assert result == CheckType.KUSTOMIZE
    assert runner.templateRendererCommand is None


def test_auto_does_not_change_existing_invalid_kubectl_fallback_behavior() -> None:
    runner = Runner()

    with mock.patch("checkov.kustomize.runner.shutil.which", return_value="/fake/tool"), \
            mock.patch("checkov.kustomize.runner.get_kubectl_version", return_value=None), \
            mock.patch("checkov.kustomize.runner.get_kustomize_version") as get_kustomize_version:
        result = runner.check_system_deps()

    assert result == CheckType.KUSTOMIZE
    assert runner.templateRendererCommand is None
    get_kustomize_version.assert_not_called()


def test_explicit_kubectl_ignores_available_kustomize() -> None:
    runner = Runner()
    runner.kustomize_command_mode = "kubectl"

    with mock.patch("checkov.kustomize.runner.shutil.which", return_value="/fake/tool") as which, \
            mock.patch("checkov.kustomize.runner.get_kubectl_version", return_value=1.30), \
            mock.patch("checkov.kustomize.runner.get_kustomize_version") as get_kustomize_version:
        result = runner.check_system_deps()

    assert result is None
    assert runner.templateRendererCommand == "kubectl"
    which.assert_called_once_with("kubectl")
    get_kustomize_version.assert_not_called()


def test_explicit_kustomize_ignores_available_kubectl() -> None:
    runner = Runner()
    runner.kustomize_command_mode = "kustomize"

    with mock.patch("checkov.kustomize.runner.shutil.which", return_value="/fake/tool") as which, \
            mock.patch("checkov.kustomize.runner.get_kustomize_version", return_value="v5.4.2"), \
            mock.patch("checkov.kustomize.runner.get_kubectl_version") as get_kubectl_version:
        result = runner.check_system_deps()

    assert result is None
    assert runner.templateRendererCommand == "kustomize"
    which.assert_called_once_with("kustomize")
    get_kubectl_version.assert_not_called()


@pytest.mark.parametrize("selection", ["kubectl", "kustomize"])
def test_explicit_selection_fails_when_selected_tool_is_missing(selection: str) -> None:
    runner = Runner()
    runner.kustomize_command_mode = selection

    with mock.patch("checkov.kustomize.runner.shutil.which", return_value=None), \
            pytest.raises(KustomizeCommandError, match=f"'{selection}' was selected"):
        runner.check_system_deps()


def test_explicit_kubectl_does_not_fallback_when_version_is_unusable() -> None:
    runner = Runner()
    runner.kustomize_command_mode = "kubectl"

    with mock.patch("checkov.kustomize.runner.shutil.which", return_value="/fake/kubectl"), \
            mock.patch("checkov.kustomize.runner.get_kubectl_version", return_value=None), \
            mock.patch("checkov.kustomize.runner.get_kustomize_version") as get_kustomize_version, \
            pytest.raises(KustomizeCommandError, match="version is unusable"):
        runner.check_system_deps()

    get_kustomize_version.assert_not_called()


def test_explicit_kustomize_does_not_fallback_when_version_is_unusable() -> None:
    runner = Runner()
    runner.kustomize_command_mode = "kustomize"

    with mock.patch("checkov.kustomize.runner.shutil.which", return_value="/fake/kustomize"), \
            mock.patch("checkov.kustomize.runner.get_kustomize_version", return_value=None), \
            mock.patch("checkov.kustomize.runner.get_kubectl_version") as get_kubectl_version, \
            pytest.raises(KustomizeCommandError, match="version is unusable"):
        runner.check_system_deps()

    get_kubectl_version.assert_not_called()


@pytest.mark.parametrize(
    ("selection", "expected_command"),
    [
        ("kubectl", ["kubectl", "kustomize"]),
        ("kustomize", ["kustomize", "build"]),
    ],
)
def test_selected_build_failure_never_invokes_fallback(
    selection: str,
    expected_command: list[str],
    tmp_path: Path,
) -> None:
    runner = Runner()
    runner.kustomize_command_mode = selection
    runner.templateRendererCommand = selection
    failed_process = mock.MagicMock(returncode=41)
    failed_process.communicate.return_value = (b"", b"controlled failure")

    with mock.patch("checkov.kustomize.runner.subprocess.Popen", return_value=failed_process) as popen:
        runner._get_kubectl_output(str(tmp_path), runner.templateRendererCommand, "base")

    popen.assert_called_once_with(
        expected_command,
        cwd=str(tmp_path),
        stdout=kustomize_runner.subprocess.PIPE,
        stderr=kustomize_runner.subprocess.PIPE,
    )


def test_no_fail_on_crash_retains_missing_tool_diagnostic(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    checkov = Checkov(argv=[
        "--directory",
        str(tmp_path),
        "--framework",
        "kustomize",
        "--kustomize-command",
        "kubectl",
        "--no-fail-on-crash",
        "--skip-download",
    ])

    with mock.patch("checkov.kustomize.runner.shutil.which", return_value=None), \
            pytest.raises(SystemExit) as exc_info:
        checkov.run()

    assert exc_info.value.code == 0
    assert "Explicit Kustomize implementation 'kubectl' was selected" in capsys.readouterr().err
