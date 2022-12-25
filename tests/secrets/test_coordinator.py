import unittest
from pathlib import Path

from checkov.runner_filter import RunnerFilter
from checkov.secrets.runner import Runner
from checkov.secrets.coordinator import secrets_coordinator


class TestCCoordinator(unittest.TestCase):

    def test_same_resources_in_report_and_coordinator(self):
        test_root_folder = f'{Path(__file__).parent}'

        report = Runner().run(
            root_folder=test_root_folder, runner_filter=RunnerFilter(framework=['secrets'])
        )
        self.assertEqual(secrets_coordinator.get_resources(), report.resources)
