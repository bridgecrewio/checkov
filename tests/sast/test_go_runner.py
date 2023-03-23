import subprocess
import unittest
from os import path


class GoRunnerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        current_dir = path.dirname(path.realpath(__file__))
        sast_core_dir = path.join(current_dir, '..', '..', 'checkov', 'sast_core')
        if not path.exists(path.join(sast_core_dir, 'library.so')):
            proc = subprocess.Popen(['make', 'build'], cwd=sast_core_dir)  # nosec
            proc.wait()

    def test_validation_pass(self):
        from checkov.sast.go_runner import run_go_library
        res = run_go_library(source_code_dir='somedir',
                             source_code_file='',
                             policy_dir='somedir',
                             policy_file='',
                             language='python')
        assert isinstance(res, dict)

    def test_validation_fail_no_policy(self):
        from checkov.sast.go_runner import run_go_library
        with self.assertRaises(Exception):
            run_go_library(source_code_dir='somedir',
                           source_code_file='',
                           policy_dir='',
                           policy_file='',
                           language='python')

    def test_validation_fail_no_code(self):
        from checkov.sast.go_runner import run_go_library
        with self.assertRaises(Exception):
            run_go_library(source_code_dir='',
                           source_code_file='',
                           policy_dir='pol',
                           policy_file='',
                           language='python')

    def test_validation_fail_lang(self):
        from checkov.sast.go_runner import run_go_library
        with self.assertRaises(Exception):
            run_go_library(source_code_dir='somedir',
                           source_code_file='',
                           policy_dir='somedir',
                           policy_file='',
                           language='')
        with self.assertRaises(Exception):
            run_go_library(source_code_dir='somedir',
                           source_code_file='',
                           policy_dir='somedir',
                           policy_file='',
                           language='js')
