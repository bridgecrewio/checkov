import unittest
from checkov.arm.checks.resource.MariaDBpublicConvertARM import check
from pathlib import Path
from checkov.arm.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestMariaDBPublicConvertARM(unittest.TestCase):
    def test_summary(self):
        test_files_dir = Path(__file__).parent / "example_MariaDBPublicConvertARM"
        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()
        passing_resources = {
              "Microsoft.DBforMariaDB/servers.pass",
        }
        failing_resources = {
               "Microsoft.DBforMariaDB/servers.fail",
         }

        passed_check_resources = {c.resource for c in report.passed_checks}
        failed_check_resources = {c.resource for c in report.failed_checks}

        assert summary["passed"] == len(passing_resources)
        assert summary["failed"] == len(failing_resources)
        assert summary["skipped"] == 0
        assert summary["parsing_errors"] == 0

        assert passed_check_resources == passing_resources
        assert failed_check_resources == failing_resources


if __name__ == '__main__':

    unittest.main()