import dis
import inspect
import unittest

import os
from pathlib import Path

from checkov.dockerfile.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestRunnerValid(unittest.TestCase):

    def test_runner_empty_dockerfile(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources/empty_dockerfile"
        runner = Runner()
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='all'))
        self.assertEqual(report.failed_checks, [])
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(report.passed_checks, [])
        self.assertEqual(report.skipped_checks, [])
        report.print_console()

    def test_runner_failing_check(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources/expose_port/fail"
        runner = Runner()
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='all',checks=['CKV_DOCKER_1']))
        self.assertEqual(len(report.failed_checks), 1)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(report.passed_checks, [])
        self.assertEqual(report.skipped_checks, [])
        report.print_console()

    def test_runner_failing_check_with_file_path(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_file_path = current_dir + "/resources/expose_port/fail/Dockerfile"
        runner = Runner()
        report = runner.run(
            files=[valid_file_path],
            external_checks_dir=None,
            runner_filter=RunnerFilter(framework="all", checks=["CKV_DOCKER_1"]),
        )
        self.assertEqual(len(report.failed_checks), 1)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(report.passed_checks, [])
        self.assertEqual(report.skipped_checks, [])
        report.print_console()

    def test_runner_passing_check(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources/expose_port/pass"
        runner = Runner()
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='all',checks=['CKV_DOCKER_1']))
        self.assertEqual(len(report.passed_checks), 1)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(report.failed_checks, [])
        self.assertEqual(report.skipped_checks, [])
        report.print_console()

    def test_runner_skip_check(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources/expose_port/skip"
        runner = Runner()
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='all',checks=['CKV_DOCKER_1']))
        self.assertEqual(len(report.skipped_checks), 1)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(report.failed_checks, [])
        self.assertEqual(report.passed_checks, [])
        report.print_console()

    def test_wrong_check_imports(self):
        wrong_imports = ["arm", "cloudformation", "helm", "kubernetes", "serverless", "terraform"]
        check_imports = []

        checks_path = Path(inspect.getfile(Runner)).parent.joinpath("checks")
        for file in checks_path.rglob("*.py"):
            with file.open() as f:
                instructions = dis.get_instructions(f.read())
                import_names = [instr.argval for instr in instructions if "IMPORT_NAME" == instr.opname]

                for import_name in import_names:
                    wrong_import = next((import_name for x in wrong_imports if x in import_name), None)
                    if wrong_import:
                        check_imports.append({file.name: wrong_import})

        assert len(check_imports) == 0, f"Wrong imports were added: {check_imports}"



if __name__ == '__main__':
    unittest.main()
