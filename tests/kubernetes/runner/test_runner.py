import dis
import inspect
import os
import unittest
from pathlib import Path

from checkov.runner_filter import RunnerFilter
from checkov.kubernetes.runner import Runner


class TestRunnerValid(unittest.TestCase):

    def test_record_relative_path_with_relative_dir(self):

        # test whether the record's repo_file_path is correct, relative to the CWD (with a / at the start).

        # this is just constructing the scan dir as normal
        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_dir_path = os.path.join(current_dir, "resources")

        # this is the relative path to the directory to scan (what would actually get passed to the -d arg)
        dir_rel_path = os.path.relpath(scan_dir_path).replace('\\', '/')

        runner = Runner()
        checks_allowlist = ['CKV_K8S_21']
        report = runner.run(root_folder=dir_rel_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='kubernetes', checks=checks_allowlist))

        all_checks = report.failed_checks + report.passed_checks
        self.assertGreater(len(all_checks), 0)  # ensure that the assertions below are going to do something
        for record in all_checks:
            # no need to join with a '/' because the CFN runner adds it to the start of the file path
            self.assertEqual(record.repo_file_path, f'/{dir_rel_path}{record.file_path}')

    def test_record_relative_path_with_abs_dir(self):

        # test whether the record's repo_file_path is correct, relative to the CWD (with a / at the start).

        # this is just constructing the scan dir as normal
        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_dir_path = os.path.join(current_dir, "resources")

        dir_rel_path = os.path.relpath(scan_dir_path).replace('\\', '/')

        dir_abs_path = os.path.abspath(scan_dir_path)

        runner = Runner()
        checks_allowlist = ['CKV_K8S_21']
        report = runner.run(root_folder=dir_abs_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='kubernetes', checks=checks_allowlist))

        all_checks = report.failed_checks + report.passed_checks
        self.assertGreater(len(all_checks), 0)  # ensure that the assertions below are going to do something
        for record in all_checks:
            # no need to join with a '/' because the CFN runner adds it to the start of the file path
            self.assertEqual(record.repo_file_path, f'/{dir_rel_path}{record.file_path}')

    def test_record_relative_path_with_relative_file(self):

        # test whether the record's repo_file_path is correct, relative to the CWD (with a / at the start).

        # this is just constructing the scan dir as normal
        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_file_path = os.path.join(current_dir, "resources", "example.yaml")

        # this is the relative path to the file to scan (what would actually get passed to the -f arg)
        file_rel_path = os.path.relpath(scan_file_path)

        runner = Runner()
        checks_allowlist = ['CKV_K8S_21']
        report = runner.run(root_folder=None, external_checks_dir=None, files=[file_rel_path],
                            runner_filter=RunnerFilter(framework='kubernetes', checks=checks_allowlist))

        all_checks = report.failed_checks + report.passed_checks
        self.assertGreater(len(all_checks), 0)  # ensure that the assertions below are going to do something
        for record in all_checks:
            # no need to join with a '/' because the CFN runner adds it to the start of the file path
            self.assertEqual(record.repo_file_path, f'/{file_rel_path}')

    def test_record_relative_path_with_abs_file(self):

        # test whether the record's repo_file_path is correct, relative to the CWD (with a / at the start).

        # this is just constructing the scan dir as normal
        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_file_path = os.path.join(current_dir, "resources", "example.yaml")

        file_rel_path = os.path.relpath(scan_file_path)
        file_abs_path = os.path.abspath(scan_file_path)

        runner = Runner()
        checks_allowlist = ['CKV_K8S_21']
        report = runner.run(root_folder=None, external_checks_dir=None, files=[file_abs_path],
                            runner_filter=RunnerFilter(framework='kubernetes', checks=checks_allowlist))

        all_checks = report.failed_checks + report.passed_checks
        self.assertGreater(len(all_checks), 0)  # ensure that the assertions below are going to do something
        for record in all_checks:
            # no need to join with a '/' because the CFN runner adds it to the start of the file path
            self.assertEqual(record.repo_file_path, f'/{file_rel_path}')

    def test_list_metadata_annotations(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_file_path = os.path.join(current_dir, "list_annotation", "example.yaml")
        file_rel_path = os.path.relpath(scan_file_path)
        runner = Runner()
        try:
            runner.run(root_folder=None, external_checks_dir=None, files=[file_rel_path],
                                runner_filter=RunnerFilter(framework='kubernetes'))
        except:
            self.assertTrue(False, "Could not run K8 runner on configuration")

    def test_wrong_check_imports(self):
        wrong_imports = ["arm", "cloudformation", "dockerfile", "helm", "serverless", "terraform"]
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

    def test_parse_with_empty_blocks(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_file_path = os.path.join(current_dir, "resources", "example_multiple.yaml")
        file_rel_path = os.path.relpath(scan_file_path)
        runner = Runner()
        try:
            report = runner.run(root_folder=None, external_checks_dir=None, files=[file_rel_path],
                       runner_filter=RunnerFilter(framework='kubernetes'))
            # just check that something was parsed and scanned
            self.assertGreater(len(report.failed_checks) + len(report.passed_checks), 0)
        except:
            self.assertTrue(False, "Could not run K8 runner on configuration")

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
