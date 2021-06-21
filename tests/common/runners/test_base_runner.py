import os
import tempfile
import unittest

from checkov.common.runners.base_runner import filter_ignored_directories


class TestBaseRunner(unittest.TestCase):

    def test_filter_ignored_directories_regex_legacy(self):
        d_names = ['bin', 'integration_tests', 'tests', 'docs', '.github', 'checkov', 'venv', '.git', 'kubernetes', '.idea']
        expected = ['bin', 'docs', 'checkov', 'venv', 'kubernetes']
        filter_ignored_directories('.', d_names, ["tests"])
        self.assertEqual(expected, d_names)

    def test_filter_ignored_directories_regex_relative_cwd(self):
        # this simulates scanning a subdirectory and applying filter logic relative to the CWD
        # for this we need to CD temporarily
        current_dir = os.path.dirname(os.path.realpath(__file__))
        old_cwd = os.path.abspath(os.curdir)

        try:
            os.chdir(current_dir)

            excluded_paths = ['dir2']

            remaining_dirs = []

            expected = {
                os.path.join('sample_dir', 'dir33'),
                os.path.join('sample_dir', 'dir1'),
                os.path.join('sample_dir', 'dir1', 'dir4'),
                os.path.join('sample_dir', 'dir11')
            }

            for root, dirs, files in os.walk('sample_dir'):
                filter_ignored_directories(root, dirs, excluded_paths)
                remaining_dirs += [os.path.join(root, d) for d in dirs]

            # we expect .terraform and all dir2 to get filtered out
            self.assertEqual(len(remaining_dirs), 4)
            self.assertEqual(set(remaining_dirs), expected)

            excluded_paths = ['dir1/dir2']

            remaining_dirs = []

            expected = {
                os.path.join('sample_dir', 'dir33'),
                os.path.join('sample_dir', 'dir1'),
                os.path.join('sample_dir', 'dir1', 'dir4'),
                os.path.join('sample_dir', 'dir11'),
                os.path.join('sample_dir', 'dir11', 'dir2'),
                os.path.join('sample_dir', 'dir33', 'dir2'),
            }

            for root, dirs, files in os.walk('sample_dir'):
                filter_ignored_directories(root, dirs, excluded_paths)
                remaining_dirs += [os.path.join(root, d) for d in dirs]

            # we expect .terraform and dir1/dir2 to get filtered out
            self.assertEqual(len(remaining_dirs), 6)
            self.assertEqual(set(remaining_dirs), expected)

            excluded_paths = ['dir../dir2']

            remaining_dirs = []

            expected = {
                os.path.join('sample_dir', 'dir33'),
                os.path.join('sample_dir', 'dir1'),
                os.path.join('sample_dir', 'dir1', 'dir4'),
                os.path.join('sample_dir', 'dir11'),
                os.path.join('sample_dir', 'dir1', 'dir2')
            }

            for root, dirs, files in os.walk('sample_dir'):
                filter_ignored_directories(root, dirs, excluded_paths)
                remaining_dirs += [os.path.join(root, d) for d in dirs]

            # we expect .terraform and dir11/dir2 and dir33/dir2 to get filtered out
            self.assertEqual(len(remaining_dirs), 5)
            self.assertEqual(set(remaining_dirs), expected)

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

        for root, dirs, files in os.walk('sample_dir'):
            filter_ignored_directories(root, dirs, excluded_paths)
            remaining_dirs += [os.path.join(root, d) for d in dirs]

        # we expect .terraform and all dir2 to get filtered out
        self.assertEqual(len(remaining_dirs), 4)
        self.assertEqual(set(remaining_dirs), expected)

        excluded_paths = ['dir1/dir2']

        remaining_dirs = []

        expected = {
            os.path.join(current_dir, 'sample_dir', 'dir33'),
            os.path.join(current_dir, 'sample_dir', 'dir1'),
            os.path.join(current_dir, 'sample_dir', 'dir1', 'dir4'),
            os.path.join(current_dir, 'sample_dir', 'dir11'),
            os.path.join(current_dir, 'sample_dir', 'dir11', 'dir2'),
            os.path.join(current_dir, 'sample_dir', 'dir33', 'dir2'),
        }

        for root, dirs, files in os.walk('sample_dir'):
            filter_ignored_directories(root, dirs, excluded_paths)
            remaining_dirs += [os.path.join(root, d) for d in dirs]

        # we expect .terraform and dir1/dir2 to get filtered out
        self.assertEqual(len(remaining_dirs), 6)
        self.assertEqual(set(remaining_dirs), expected)

        excluded_paths = ['dir../dir2']

        remaining_dirs = []

        expected = {
            os.path.join(current_dir, 'sample_dir', 'dir33'),
            os.path.join(current_dir, 'sample_dir', 'dir1'),
            os.path.join(current_dir, 'sample_dir', 'dir1', 'dir4'),
            os.path.join(current_dir, 'sample_dir', 'dir11'),
            os.path.join(current_dir, 'sample_dir', 'dir1', 'dir2')
        }

        for root, dirs, files in os.walk('sample_dir'):
            filter_ignored_directories(root, dirs, excluded_paths)
            remaining_dirs += [os.path.join(root, d) for d in dirs]

        # we expect .terraform and dir11/dir2 and dir33/dir2 to get filtered out
        self.assertEqual(len(remaining_dirs), 5)
        self.assertEqual(set(remaining_dirs), expected)



