import os
import unittest
from typing import Optional, List

from checkov.common.output.report import Report
from checkov.common.runners.base_runner import filter_ignored_paths, BaseRunner
from checkov.runner_filter import RunnerFilter


class TestBaseRunner(unittest.TestCase):

    def test_filter_ignored_directories_regex_legacy(self):
        d_names = ['bin', 'integration_tests', 'tests', 'docs', '.github', 'checkov', 'venv', '.git', 'kubernetes', '.idea']
        expected = ['bin', 'docs', 'checkov', 'venv', 'kubernetes']
        filter_ignored_paths('.', d_names, ["tests"])
        self.assertEqual(expected, d_names)

    def test_filter_ignored_directories_regex_relative_cwd(self):
        # this simulates scanning a subdirectory and applying filter logic relative to the CWD
        # for this we need to CD temporarily
        current_dir = os.path.dirname(os.path.realpath(__file__))
        old_cwd = os.path.abspath(os.curdir)

        try:
            os.chdir(current_dir)

            excluded_paths = ['dir2', os.path.join('dir1', 'file1.tf')]

            remaining_dirs = []
            remaining_files = []

            expected_dirs = {
                os.path.join('sample_dir', 'dir33'),
                os.path.join('sample_dir', 'dir1'),
                os.path.join('sample_dir', 'dir1', 'dir4'),
                os.path.join('sample_dir', 'dir11')
            }

            expected_files = {
                os.path.join('sample_dir', 'dir33', 'file2.tf'),
                os.path.join('sample_dir', 'dir1', 'dir4', 'file3.tf'),
            }

            for root, dirs, files in os.walk('sample_dir'):
                filter_ignored_paths(root, dirs, excluded_paths)
                filter_ignored_paths(root, files, excluded_paths)
                remaining_dirs += [os.path.join(root, d) for d in dirs]
                remaining_files += [os.path.join(root, f) for f in files]

            # we expect .terraform and all dir2 to get filtered out
            # also dir1/file1
            self.assertEqual(set(remaining_dirs), expected_dirs)
            self.assertEqual(set(remaining_files), expected_files)

            excluded_paths = [os.path.join('dir1', 'dir2')]

            remaining_dirs = []
            remaining_files = []

            expected_dirs = {
                os.path.join('sample_dir', 'dir33'),
                os.path.join('sample_dir', 'dir1'),
                os.path.join('sample_dir', 'dir1', 'dir4'),
                os.path.join('sample_dir', 'dir11'),
                os.path.join('sample_dir', 'dir11', 'dir2'),
                os.path.join('sample_dir', 'dir33', 'dir2'),
            }

            expected_files = {
                os.path.join('sample_dir', 'dir33', 'file2.tf'),
                os.path.join('sample_dir', 'dir1', 'file1.tf'),
                os.path.join('sample_dir', 'dir1', 'dir4', 'file3.tf'),
                os.path.join('sample_dir', 'dir11', 'dir2', 'file4.tf'),
                os.path.join('sample_dir', 'dir33', 'dir2', 'file5.tf')
            }

            for root, dirs, files in os.walk('sample_dir'):
                filter_ignored_paths(root, dirs, excluded_paths)
                filter_ignored_paths(root, files, excluded_paths)
                remaining_dirs += [os.path.join(root, d) for d in dirs]
                remaining_files += [os.path.join(root, f) for f in files]

            # we expect .terraform and dir1/dir2 to get filtered out
            self.assertEqual(set(remaining_dirs), expected_dirs)
            self.assertEqual(set(remaining_files), expected_files)

            excluded_paths = [os.path.join('dir..', 'dir2')]

            remaining_dirs = []
            remaining_files = []

            expected_dirs = {
                os.path.join('sample_dir', 'dir33'),
                os.path.join('sample_dir', 'dir1'),
                os.path.join('sample_dir', 'dir1', 'dir4'),
                os.path.join('sample_dir', 'dir11'),
                os.path.join('sample_dir', 'dir1', 'dir2')
            }

            expected_files = {
                os.path.join('sample_dir', 'dir1', 'dir2', 'file2.tf'),
                os.path.join('sample_dir', 'dir1', 'file1.tf'),
                os.path.join('sample_dir', 'dir33', 'file2.tf'),
                os.path.join('sample_dir', 'dir1', 'dir4', 'file3.tf')
            }

            for root, dirs, files in os.walk('sample_dir'):
                filter_ignored_paths(root, dirs, excluded_paths)
                filter_ignored_paths(root, files, excluded_paths)
                remaining_dirs += [os.path.join(root, d) for d in dirs]
                remaining_files += [os.path.join(root, f) for f in files]

            # we expect .terraform and dir11/dir2 and dir33/dir2 to get filtered out
            self.assertEqual(set(remaining_dirs), expected_dirs)
            self.assertEqual(set(remaining_files), expected_files)

        finally:
            os.chdir(old_cwd)

    def test_filter_ignored_directories_regex_absolute_cwd(self):
        # this simulates scanning a subdirectory and applying filter logic using an absolute path
        current_dir = os.path.dirname(os.path.realpath(__file__))

        excluded_paths = ['dir2']

        remaining_dirs = []

        expected = {
            os.path.join(current_dir, 'sample_dir', 'dir33'),
            os.path.join(current_dir, 'sample_dir', 'dir1'),
            os.path.join(current_dir, 'sample_dir', 'dir1', 'dir4'),
            os.path.join(current_dir, 'sample_dir', 'dir11')
        }

        for root, dirs, files in os.walk(os.path.join(current_dir, 'sample_dir')):
            filter_ignored_paths(root, dirs, excluded_paths)
            remaining_dirs += [os.path.join(root, d) for d in dirs]

        # we expect .terraform and all dir2 to get filtered out
        self.assertEqual(set(remaining_dirs), expected)

        excluded_paths = [os.path.join('dir1', 'dir2')]

        remaining_dirs = []

        expected = {
            os.path.join(current_dir, 'sample_dir', 'dir33'),
            os.path.join(current_dir, 'sample_dir', 'dir1'),
            os.path.join(current_dir, 'sample_dir', 'dir1', 'dir4'),
            os.path.join(current_dir, 'sample_dir', 'dir11'),
            os.path.join(current_dir, 'sample_dir', 'dir11', 'dir2'),
            os.path.join(current_dir, 'sample_dir', 'dir33', 'dir2'),
        }

        for root, dirs, files in os.walk(os.path.join(current_dir, 'sample_dir')):
            filter_ignored_paths(root, dirs, excluded_paths)
            remaining_dirs += [os.path.join(root, d) for d in dirs]

        # we expect .terraform and dir1/dir2 to get filtered out
        self.assertEqual(set(remaining_dirs), expected)

        excluded_paths = [os.path.join('dir..', 'dir2')]

        remaining_dirs = []

        expected = {
            os.path.join(current_dir, 'sample_dir', 'dir33'),
            os.path.join(current_dir, 'sample_dir', 'dir1'),
            os.path.join(current_dir, 'sample_dir', 'dir1', 'dir4'),
            os.path.join(current_dir, 'sample_dir', 'dir11'),
            os.path.join(current_dir, 'sample_dir', 'dir1', 'dir2')
        }

        for root, dirs, files in os.walk(os.path.join(current_dir, 'sample_dir')):
            filter_ignored_paths(root, dirs, excluded_paths)
            remaining_dirs += [os.path.join(root, d) for d in dirs]

        # we expect .terraform and dir11/dir2 and dir33/dir2 to get filtered out
        self.assertEqual(set(remaining_dirs), expected)

    def test_filter_ignored_directories_by_values(self):
        # this simulates scanning a subdirectory and applying filter logic using an absolute path
        current_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'filter_ignored_directories_by_values')
        excluded_paths = ['dir2++']
        remaining_dirs = []
        expected = {
            os.path.join(current_dir, 'dir33'),
            os.path.join(current_dir, 'dir1'),
            os.path.join(current_dir, 'dir1', 'dir4'),
            os.path.join(current_dir, 'dir11')
        }

        for root, dirs, files in os.walk(current_dir):
            filter_ignored_paths(root, dirs, excluded_paths)
            remaining_dirs += [os.path.join(root, d) for d in dirs]

        # we expect .terraform and all dir2 to get filtered out
        self.assertEqual(set(remaining_dirs), expected)

        excluded_paths = [os.path.join('dir1', 'dir2++')]

        remaining_dirs = []

        expected = {
            os.path.join(current_dir, 'dir33'),
            os.path.join(current_dir, 'dir1'),
            os.path.join(current_dir, 'dir1', 'dir4'),
            os.path.join(current_dir, 'dir11'),
            os.path.join(current_dir, 'dir11', 'dir2++'),
            os.path.join(current_dir, 'dir33', 'dir2++'),
        }

        for root, dirs, files in os.walk(current_dir):
            filter_ignored_paths(root, dirs, excluded_paths)
            remaining_dirs += [os.path.join(root, d) for d in dirs]

        # we expect .terraform and dir1/dir2 to get filtered out
        self.assertEqual(set(remaining_dirs), expected)

    def test_file_filter(self):
        runner = Runner()

        self.assertTrue(runner.should_scan_file('xyz.txt'))  # if a filename or extension list is not provided, return True

        runner.file_extensions = ['.json', '.yaml']

        self.assertTrue(runner.should_scan_file('test.json'))
        self.assertTrue(runner.should_scan_file('test.yaml'))
        self.assertTrue(runner.should_scan_file('absolute/path/test.yaml'))
        self.assertFalse(runner.should_scan_file('test.tf'))

        runner.file_names = ['Dockerfile', 'requirements.txt']

        self.assertTrue(runner.should_scan_file('test.json'))
        self.assertTrue(runner.should_scan_file('test.yaml'))
        self.assertTrue(runner.should_scan_file('requirements.txt'))
        self.assertTrue(runner.should_scan_file('Dockerfile'))
        self.assertTrue(runner.should_scan_file('absolute/path/test.yaml'))
        self.assertFalse(runner.should_scan_file('test.tf'))

        runner.file_extensions = []

        self.assertFalse(runner.should_scan_file('test.json'))
        self.assertFalse(runner.should_scan_file('test.yaml'))
        self.assertTrue(runner.should_scan_file('requirements.txt'))
        self.assertTrue(runner.should_scan_file('Dockerfile'))
        self.assertFalse(runner.should_scan_file('absolute/path/test.yaml'))
        self.assertFalse(runner.should_scan_file('test.tf'))


class Runner(BaseRunner):
    def run(
            self,
            root_folder: str,
            external_checks_dir: Optional[List[str]] = None,
            files: Optional[List[str]] = None,
            runner_filter: RunnerFilter = RunnerFilter(),
            collect_skip_comments: bool = True,
    ) -> Report:
        pass