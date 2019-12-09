import os
import unittest

from checkov.terraform.runner import Runner

dir_path = os.path.dirname(os.path.realpath(__file__))


class TestRunner(unittest.TestCase):

    def test_runner(self):
        runner = Runner()
        report = runner.run(root_folder=dir_path)
        report_json = report.get_json()
        self.assertTrue(isinstance(report_json, str))
        self.assertIsNotNone(report_json)
        self.assertIsNotNone(report.get_test_suites())
        summary = report.get_summary()
        self.assertGreaterEqual(summary['passed'], 1)
        self.assertGreaterEqual(summary['failed'], 1)
        self.assertEqual(summary["parsing_errors"], 0)
        report.print_json()
        report.print_console()
        report.print_junit_xml()


if __name__ == '__main__':
    unittest.main()
