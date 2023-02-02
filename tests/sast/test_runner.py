from checkov.common.sast.enums import SastLanguages
from checkov.sast.checks.base_registry import Registry
from checkov.sast.runner import Runner
import pathlib
import os


def test_sast_runner_python():
    checks_dir = os.path.join(pathlib.Path(__file__).parent.resolve(), 'checks')
    runner = Runner()

    runner.run()

def test_sast_runner_get_semgrep_output():
    pass


def test_sast_runner_get_report():
    pass


def test_sast_runner_get_code_block():
    runner = Runner()
    lines = ['a', 'b', 'c', 'd']
    result = runner._get_code_block(lines, 2)
    assert result == [(2, 'a'), (3, 'b'), (4, 'c'), (5, 'd')]