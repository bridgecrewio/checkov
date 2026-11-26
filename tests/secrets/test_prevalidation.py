from __future__ import annotations

import os
from pathlib import Path
from unittest import mock

import pytest

from checkov.common.bridgecrew.platform_integration import bc_integration
from checkov.runner_filter import RunnerFilter
from checkov.secrets.plugins.custom_regex_detector import (
    DETECT_SECRETS_PREVALIDATION_ENV_VAR,
    PREVALIDATION_ENV_VAR,
    CustomRegexDetector,
)
from checkov.secrets.runner import Runner


def _policy(incident_id: str, code: str) -> dict:
    return {
        "incidentId": incident_id,
        "category": "Secrets",
        "severity": "MEDIUM",
        "incidentType": "Violation",
        "title": incident_id,
        "guideline": "test",
        "laceworkViolationId": None,
        "prowlerCheckId": None,
        "checkovCheckId": None,
        "resourceTypes": ["aws_instance"],
        "provider": "AWS",
        "remediationIds": [],
        "customerName": "test",
        "isCustom": True,
        "code": code,
        "descriptiveTitle": None,
        "constructiveTitle": None,
        "pcPolicyId": None,
        "additionalPcPolicyIds": None,
        "pcSeverity": None,
        "sourceIncidentId": None,
    }


POLICIES = [
    _policy("prevalidation_single", "definition:\n  cond_type: secrets\n  value:\n  - (?i)acmeint_([a-z0-9]{32})\n"),
    _policy("prevalidation_other", "definition:\n  cond_type: secrets\n  value:\n  - (?i)zetavendor_key\\s*=\\s*([a-z0-9]{20})\n"),
    _policy(
        "prevalidation_multiline",
        "definition:\n  cond_type: secrets\n  multiline: true\n  prerun:\n  - (?i)(?:algolia)\n  value:\n"
        "  - (?i)(?:algolia)(?:.|[\\n\\r]){0,80}([A-Za-z0-9]{32})\n",
    ),
]

FILES = {
    "service.py": 'TOKEN = "acmeint_0bpf0p6o8tieai29cynzwtvt3xoh6rjf"\n',
    "Dockerfile.search": "ENV ALGOLIA_APP=app\nENV KEY=\\\n    a1B2c3D4e5F6g7H8i9J0k1L2m3N4o5P6\n",
    "notes.txt": "nothing to see here\njust plain text\n",
}


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    for name, content in FILES.items():
        (tmp_path / name).write_text(content)
    return tmp_path


@pytest.fixture(autouse=True)
def custom_policies():
    previous = bc_integration.customer_run_config_response
    bc_integration.customer_run_config_response = {"secretsPolicies": POLICIES}
    yield
    bc_integration.customer_run_config_response = previous


def _prevalidation_env(enabled: bool) -> mock._patch_dict:
    return mock.patch.dict(os.environ, {PREVALIDATION_ENV_VAR: "true" if enabled else "false"})


def _scan(root: Path, enabled: bool) -> list[tuple[str, str, int]]:
    with _prevalidation_env(enabled):
        report = Runner().run(
            root_folder=str(root),
            runner_filter=RunnerFilter(framework=["secrets"], enable_secret_scan_all_files=True),
        )
    return sorted(
        (check.check_id, Path(check.file_path).name, check.file_line_range[0])
        for check in report.failed_checks
        if check.check_id.startswith("prevalidation_")
    )


def test_same_findings_with_and_without_prevalidation(repo: Path) -> None:
    disabled = _scan(repo, enabled=False)
    assert {check_id for check_id, _, _ in disabled} == {"prevalidation_single", "prevalidation_multiline"}
    assert _scan(repo, enabled=True) == disabled


def test_active_rules_only_keep_rules_whose_literals_appear(repo: Path) -> None:
    with _prevalidation_env(True):
        detector = CustomRegexDetector()
        single, multiline = detector._active_rules(str(repo / "service.py"))
        assert {r.pattern for r in single} == {"(?i)acmeint_([a-z0-9]{32})"}
        assert not multiline

        single, multiline = detector._active_rules(str(repo / "notes.txt"))
        assert not single
        assert not multiline


def test_active_rules_disabled_runs_everything(repo: Path) -> None:
    with _prevalidation_env(False):
        assert CustomRegexDetector()._active_rules(str(repo / "notes.txt")) is None


@pytest.mark.parametrize(("enabled", "expected"), [(True, "1"), (False, "0")])
def test_detect_secrets_prevalidation_follows_checkov_flag(enabled: bool, expected: str) -> None:
    preset = {DETECT_SECRETS_PREVALIDATION_ENV_VAR: "1" if not enabled else "0"}
    with mock.patch.dict(os.environ, preset), _prevalidation_env(enabled):
        CustomRegexDetector()
        assert os.environ[DETECT_SECRETS_PREVALIDATION_ENV_VAR] == expected
