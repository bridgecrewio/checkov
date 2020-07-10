import os
import unittest

from checkov.cloudformation.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestCfnYaml(unittest.TestCase):

    def test_skip_parsing(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files = f'{current_dir}/skip.yaml'
        report = Runner().run(None, files=[test_files], runner_filter=RunnerFilter())
        summary = report.get_summary()

        self.assertEqual(summary['passed'], 1)
        self.assertEqual(summary['failed'], 0)
        self.assertEqual(summary['skipped'], 1)
        self.assertEqual(summary['parsing_errors'], 0)

if __name__ == '__main__':
    unittest.main()
