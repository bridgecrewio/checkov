from __future__ import annotations

from pathlib import Path

import configargparse
import pytest

from checkov.common.util.ext_argument_parser import ExtArgumentParser


def _parser(*, config_file: str | None = None) -> ExtArgumentParser:
    parser = ExtArgumentParser(
        config_file_parser_class=configargparse.YAMLConfigFileParser,
        default_config_files=[config_file] if config_file else [],
    )
    parser.add_parser_args()
    return parser


def test_kustomize_command_defaults_to_auto() -> None:
    assert _parser().parse_args([]).kustomize_command == "auto"


def test_kustomize_command_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CKV_KUSTOMIZE_COMMAND", "kustomize")
    assert _parser().parse_args([]).kustomize_command == "kustomize"


def test_kustomize_command_from_config_file(tmp_path: Path) -> None:
    config_file = tmp_path / "checkov.yml"
    config_file.write_text("kustomize-command: kubectl\n")

    assert _parser(config_file=str(config_file)).parse_args([]).kustomize_command == "kubectl"


def test_cli_overrides_environment_and_config(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    config_file = tmp_path / "checkov.yml"
    config_file.write_text("kustomize-command: auto\n")
    monkeypatch.setenv("CKV_KUSTOMIZE_COMMAND", "kubectl")

    result = _parser(config_file=str(config_file)).parse_args(["--kustomize-command", "kustomize"])

    assert result.kustomize_command == "kustomize"


def test_environment_overrides_config(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    config_file = tmp_path / "checkov.yml"
    config_file.write_text("kustomize-command: kubectl\n")
    monkeypatch.setenv("CKV_KUSTOMIZE_COMMAND", "kustomize")

    assert _parser(config_file=str(config_file)).parse_args([]).kustomize_command == "kustomize"


def test_unknown_kustomize_command_is_rejected() -> None:
    with pytest.raises(SystemExit) as exc_info:
        _parser().parse_args(["--kustomize-command", "shell-string"])

    assert exc_info.value.code == 2


def test_unknown_kustomize_command_from_environment_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CKV_KUSTOMIZE_COMMAND", "shell-string")

    with pytest.raises(SystemExit) as exc_info:
        _parser().parse_args([])

    assert exc_info.value.code == 2


def test_show_config_records_selected_value_and_command_line_source() -> None:
    parser = _parser()

    parser.parse_args(["--kustomize-command", "kubectl"])
    rendered_config = parser.format_values()

    assert "Command Line Args:" in rendered_config
    assert "--kustomize-command kubectl" in rendered_config


def test_create_config_writes_selected_value(tmp_path: Path) -> None:
    config_file = tmp_path / "generated-checkov.yml"

    with pytest.raises(SystemExit) as exc_info:
        _parser().parse_args([
            "--kustomize-command",
            "kustomize",
            "--create-config",
            str(config_file),
        ])

    assert exc_info.value.code == 0
    assert "kustomize-command: kustomize\n" in config_file.read_text()
