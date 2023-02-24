from checkov.runner_filter import RunnerFilter
from checkov.sast.consts import SastLanguages
from checkov.sast.checks_infra.base_registry import Registry
import pathlib
import os
import unittest

python_rule = {'id': 'CKV_SAST_1', 'message': 'module setting superuser port', 'severity': 'INFO',
                       'languages': ['python'], 'metadata': {'name': 'superuser port',
                                                             'cwe': 'CWE-289: Authentication Bypass by Alternate Name',
                                                             'check_file': 'python_rule.yaml'},
                       'patterns': [{'pattern': 'set_port($ARG)'}, {'metavariable-comparison': {
                           'metavariable': '$ARG', 'comparison': '$ARG < 1024'}}]}


java_rule = {'id': 'seam-log-injection', 'message': 'Seam Logging API support an expression language to introduce bean property to log messages. The expression language can also be the source to unwanted code execution. In this context, an expression is built with a dynamic value. The source of the value(s) should be verified to avoid that unfiltered values fall into this risky code evaluation.',
             'severity': 'ERROR', 'languages': ['java'], 'metadata': {
                'name': 'seam log injection',
                'cwe': "CWE-95: Improper Neutralization of Directives in Dynamically Evaluated Code ('Eval Injection')",
                'owasp': 'A03:2021 - Injection',
                'check_file': 'java_rule.yaml'},
                'patterns': [{'pattern': '$LOG.$INFO($X + $Y,...)'},
                    {'pattern-either': [{'pattern-inside': 'import org.jboss.seam.log.Log\n...\n'},
                          {'pattern-inside': 'org.jboss.seam.log.Log $LOG = ...\n...\n'}]},
                          {'metavariable-regex': {'metavariable': '$INFO',
                                                  'regex': '(debug|error|fatal|info|trace|warn)'}}]}
class TestRegistry(unittest.TestCase):
    def test_sast_registry_only_python(self):
        checks_dir = os.path.join(pathlib.Path(__file__).parent.resolve(), '..', 'checks')
        registry = Registry(checks_dir)

        registry.load_rules([SastLanguages.PYTHON])
        registry.rules
        assert registry.rules == [python_rule]


    def test_sast_registry_with_external_dir(self):
        checks_dir = os.path.join(pathlib.Path(__file__).parent.resolve(), '..', 'checks')
        external_checks_dir = os.path.join(pathlib.Path(__file__).parent.resolve(), '..', 'external_checks')
        registry = Registry(checks_dir)

        registry.load_rules({SastLanguages.PYTHON})
        registry.load_external_rules(external_checks_dir, {SastLanguages.JAVA})
        assert registry.rules == [python_rule, java_rule]

    def test_sast_skip_checks(self):
        checks_dir = os.path.join(pathlib.Path(__file__).parent.resolve(), '..', 'checks')
        external_checks_dir = os.path.join(pathlib.Path(__file__).parent.resolve(), '..', 'external_checks')
        registry = Registry(checks_dir)
        runner_filter = RunnerFilter(framework=['sast'], skip_checks=['CKV_SAST_1'])
        registry.set_runner_filter(runner_filter)

        registry.load_rules(runner_filter.sast_languages)
        registry.load_external_rules(external_checks_dir, runner_filter.sast_languages)

        assert registry.rules == [java_rule]
