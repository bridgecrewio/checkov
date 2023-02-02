from checkov.common.sast.enums import SastLanguages
from checkov.sast.checks.base_registry import Registry
import pathlib
import os


def test_sast_registry_only_python():
    checks_dir = os.path.join(pathlib.Path(__file__).parent.resolve(), 'checks')
    registry = Registry(checks_dir)

    sast_langs = [SastLanguages.PYTHON]
    registry.load_checks( sast_langs)
    assert registry.checks == [os.path.join(checks_dir, 'python_rule.yaml')]
    

def test_sast_registry_only_java():
    checks_dir = os.path.join(pathlib.Path(__file__).parent.resolve(), 'checks')
    registry = Registry(checks_dir)

    sast_langs = [SastLanguages.JAVA]
    registry.load_checks(sast_langs)
    assert registry.checks == [os.path.join(checks_dir, 'java_rule.yaml')]
    

def test_sast_registry_all():
    checks_dir = os.path.join(pathlib.Path(__file__).parent.resolve(), 'checks')
    registry = Registry(checks_dir)

    sast_langs = [SastLanguages.JAVA, SastLanguages.PYTHON]
    registry.load_checks(sast_langs)
    assert registry.checks == [os.path.join(checks_dir, 'java_rule.yaml'), os.path.join(checks_dir, 'python_rule.yaml')]
