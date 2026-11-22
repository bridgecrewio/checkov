"""Spawn-mode secrets scanning must produce the same findings as thread mode.

Spawned workers start with blank memory, so any state the parent builds up
(detect-secrets settings, platform secrets policies) has to be handed to them
explicitly. These tests compare both modes on the same input to catch any
state that is not forwarded.
"""
import os
import sys
import unittest
from typing import Any, Dict, List, Set, Tuple
from unittest import mock

from checkov.common.bridgecrew.platform_integration import bc_integration
from checkov.common.output.report import Report
from checkov.runner_filter import RunnerFilter
from checkov.secrets import runner as secrets_runner
from checkov.secrets.runner import Runner, _init_secrets_worker

CUSTOM_REGEX_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "custom_regex_detector")


def _platform_policy(incident_id: str, regex: str, checkov_check_id: Any = None, is_custom: bool = True) -> Dict[str, Any]:
    return {
        "incidentId": incident_id,
        "category": "Secrets",
        "severity": "MEDIUM",
        "incidentType": "Violation",
        "title": incident_id,
        "guideline": "test",
        "checkovCheckId": checkov_check_id,
        "conditionQuery": {"value": [regex], "cond_type": "secrets"},
        "isCustom": is_custom,
        "code": None,
    }


PLATFORM_POLICIES: List[Dict[str, Any]] = [
    # organisation-defined policies
    _platform_policy("org_policy_1", r"(?:^|\W)HANA(?:$|\W)"),
    _platform_policy("org_policy_2", r"(?:^|\W)LIR(?:$|\W)"),
    # platform-managed policy that maps to a checkov check id
    _platform_policy("BC_GIT_TEST", r"5FP0NmFYz81U32XdjNb42762", checkov_check_id="CKV_SECRET_TEST", is_custom=False),
]


def _findings(report: Report) -> Set[Tuple[str, str, Tuple[int, ...]]]:
    return {
        (record.check_id, record.file_path, tuple(record.file_line_range))
        for record in report.failed_checks
    }


class TestSecretsSpawnModeParity(unittest.TestCase):
    def setUp(self) -> None:
        self._original_run_config = bc_integration.customer_run_config_response
        bc_integration.customer_run_config_response = {"secretsPolicies": PLATFORM_POLICIES}

    def tearDown(self) -> None:
        bc_integration.customer_run_config_response = self._original_run_config

    def _run(self, mode: str) -> Report:
        with mock.patch.object(secrets_runner, "SECRETS_PARALLEL_MODE", mode):
            return Runner().run(
                root_folder=CUSTOM_REGEX_DIR,
                runner_filter=RunnerFilter(framework=["secrets"], enable_secret_scan_all_files=True),
            )

    @unittest.skipIf(getattr(sys, "frozen", False), "spawn mode is disabled in frozen builds")
    def test_spawn_and_thread_report_the_same_findings(self) -> None:
        thread_findings = _findings(self._run("thread"))
        spawn_findings = _findings(self._run("spawn"))

        platform_check_ids = {"org_policy_1", "org_policy_2", "CKV_SECRET_TEST"}
        # sanity: the fixture must exercise the platform policies, otherwise the comparison proves nothing
        self.assertTrue(platform_check_ids & {check_id for check_id, _, _ in thread_findings})
        self.assertEqual(thread_findings, spawn_findings)


class TestInitSecretsWorker(unittest.TestCase):
    """Simulates a freshly spawned worker: no platform run config in memory."""

    def setUp(self) -> None:
        self._original_run_config = bc_integration.customer_run_config_response
        bc_integration.customer_run_config_response = None

    def tearDown(self) -> None:
        bc_integration.customer_run_config_response = self._original_run_config

    def test_worker_receives_platform_policies(self) -> None:
        from checkov.secrets.plugins.custom_regex_detector import CustomRegexDetector

        _init_secrets_worker({"plugins_used": [{"name": "AWSKeyDetector"}]}, [], PLATFORM_POLICIES)

        self.assertEqual(bc_integration.customer_run_config_response, {"secretsPolicies": PLATFORM_POLICIES})
        self.assertEqual(len(CustomRegexDetector().regex_to_metadata), len(PLATFORM_POLICIES))

    def test_worker_without_platform_policies(self) -> None:
        _init_secrets_worker({"plugins_used": [{"name": "AWSKeyDetector"}]}, [], None)

        self.assertIsNone(bc_integration.customer_run_config_response)


if __name__ == "__main__":
    unittest.main()
