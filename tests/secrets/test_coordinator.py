import unittest
from pathlib import Path

from checkov.runner_filter import RunnerFilter
from checkov.secrets.runner import Runner


class TestCoordinator(unittest.TestCase):

    def test_same_resources_in_report_and_coordinator(self):
        test_root_folder = f'{Path(__file__).parent}'

        secret_runner = Runner()
        report = secret_runner.run(
            root_folder=test_root_folder, runner_filter=RunnerFilter(framework=['secrets'])
        )
        secrets_resources_in_coordinator = set(secret_runner.secrets_coordinator.get_resources())
        failed_resources_from_report = set(f"{record.file_path}:{record.resource}" for record in report.failed_checks)
        self.assertEqual(secrets_resources_in_coordinator, failed_resources_from_report)
