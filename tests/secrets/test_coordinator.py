import unittest
from pathlib import Path

from checkov.runner_filter import RunnerFilter
from checkov.secrets.runner import Runner
from checkov.secrets.coordinator import secrets_coordinator


class TestCoordinator(unittest.TestCase):

    def test_same_resources_in_report_and_coordinator(self):
        test_root_folder = f'{Path(__file__).parent}'

        report = Runner().run(
            root_folder=test_root_folder, runner_filter=RunnerFilter(framework=['secrets'])
        )
        secrets_resources_in_coordinator = secrets_coordinator.get_resources()
        failed_resources_from_report = set(f"{record.file_abs_path}:{record.resource}" for record in report.failed_checks)
        self.assertEqual(secrets_resources_in_coordinator, failed_resources_from_report)
