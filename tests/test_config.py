import unittest

import argparse

from checkov.config import CheckovConfig
from checkov.main import add_parser_args


class TestRunnerFilter(unittest.TestCase):
    def assertConfig(self, expected: dict, config: CheckovConfig, message_prefix=''):
        if message_prefix:
            message_prefix = message_prefix + ': '
        self.assertEqual(expected['source'], config.source,
                         f'{message_prefix}Expect source to be {expected["source"]} but got {config.source}')
        self.assertIsInstance(config.directory, frozenset,
                              f'{message_prefix}Expect directory to be a set but got {type(config.directory)}')
        self.assertSetEqual(expected['directory'], config.directory,
                            f'{message_prefix}Expect directory to be {expected["directory"]} but got '
                            f'{config.directory}')
        self.assertIsInstance(config.file, frozenset,
                              f'{message_prefix}Expect file to be a set but got {type(config.file)}')
        self.assertSetEqual(expected['file'], config.file,
                            f'{message_prefix}Expect file to be {expected["file"]} but got {config.file}')
        self.assertIsInstance(config.external_checks_dir, frozenset,
                              f'{message_prefix}Expect external_checks_dir to be a set but got '
                              f'{type(config.external_checks_dir)}')
        self.assertSetEqual(expected['external_checks_dir'], config.external_checks_dir,
                            f'{message_prefix}Expect external_checks_dir to be {expected["external_checks_dir"]} but '
                            f'got {config.external_checks_dir}')
        self.assertIsInstance(config.external_checks_git, frozenset,
                              f'{message_prefix}Expect external_checks_git to be a set but got '
                              f'{type(config.external_checks_git)}')
        self.assertSetEqual(expected['external_checks_git'], config.external_checks_git,
                            f'{message_prefix}Expect external_checks_git to be {expected["external_checks_git"]} but '
                            f'got {config.external_checks_git}')
        self.assertEqual(expected['_output'], config._output,
                         f'{message_prefix}Expect _output to be {expected["_output"]} but got {config._output}')
        self.assertEqual(expected['output'], config.output,
                         f'{message_prefix}Expect output to be {expected["output"]} but got {config.output}')
        self.assertEqual(expected['_no_guide'], config._no_guide,
                         f'{message_prefix}Expect _no_guide to be {expected["_no_guide"]} but got {config._no_guide}')
        self.assertEqual(expected['no_guide'], config.no_guide,
                         f'{message_prefix}Expect no_guide to be {expected["no_guide"]} but got {config.no_guide}')
        self.assertEqual(expected['_quiet'], config._quiet,
                         f'{message_prefix}Expect _quiet to be {expected["_quiet"]} but got {config._quiet}')
        self.assertEqual(expected['quiet'], config.quiet,
                         f'{message_prefix}Expect quiet to be {expected["quiet"]} but got {config.quiet}')
        self.assertEqual(expected['_framework'], config._framework,
                         f'{message_prefix}Expect _framework to be {expected["_framework"]} but got '
                         f'{config._framework}')
        self.assertEqual(expected['framework'], config.framework,
                         f'{message_prefix}Expect framework to be {expected["framework"]} but got {config.framework}')
        self.assertEqual(expected['check'], config.check,
                         f'{message_prefix}Expect check to be {expected["check"]} but got {config.check}')
        self.assertEqual(expected['skip_check'], config.skip_check,
                         f'{message_prefix}Expect skip_check to be {expected["skip_check"]} but got '
                         f'{config.skip_check}')
        self.assertEqual(expected['_soft_fail'], config._soft_fail,
                         f'{message_prefix}Expect _soft_fail to be {expected["_soft_fail"]} but got '
                         f'{config._soft_fail}')
        self.assertEqual(expected['soft_fail'], config.soft_fail,
                         f'{message_prefix}Expect soft_fail to be {expected["soft_fail"]} but got {config.soft_fail}')
        self.assertEqual(expected['repo_id'], config.repo_id,
                         f'{message_prefix}Expect repo_id to be {expected["repo_id"]} but got {config.repo_id}')
        self.assertEqual(expected['_branch'], config._branch,
                         f'{message_prefix}Expect _branch to be {expected["_branch"]} but got {config._branch}')
        self.assertEqual(expected['branch'], config.branch,
                         f'{message_prefix}Expect branch to be {expected["branch"]} but got {config.branch}')

    # TODO add a test that checks if cli can override --check and --skip-check
    def test_config_creation_no_args(self):
        parser = argparse.ArgumentParser()
        add_parser_args(parser)
        args = parser.parse_args([])
        config = CheckovConfig.from_args(args)
        self.assertConfig({
            'source': 'args',
            'directory': set(),
            'file': set(),
            'external_checks_dir': set(),
            'external_checks_git': set(),
            '_output': None,
            'output': 'cli',
            '_no_guide': None,
            'no_guide': False,
            '_quiet': None,
            'quiet': False,
            '_framework': None,
            'framework': 'all',
            'check': None,
            'skip_check': None,
            '_soft_fail': None,
            'soft_fail': False,
            'repo_id': None,
            '_branch': None,
            'branch': 'master',
        }, config)

    def test_config_creation_short_args(self):
        parser = argparse.ArgumentParser()
        add_parser_args(parser)
        args = parser.parse_args([
            '-d', '/a1',
            '-d', '/a1',
            '-d', '/b1',
            '--directory', '/a2',
            '--directory', '/a2',
            '--directory', '/b2',
            '-f', '/a3',
            '-f', '/a3',
            '-f', '/b3',
            '--file', '/a4',
            '--file', '/a4',
            '--file', '/b4',
            '--external-checks-dir', '/a5',
            '--external-checks-dir', '/a5',
            '--external-checks-dir', '/b5',
            '--external-checks-git', '/a6',
            '--external-checks-git', '/a6',
            '--external-checks-git', '/b6',
            '-o', 'json',
            '--no-guide',
            '--quiet',
            '--framework', 'kubernetes',
            '-c', 'CKV_AWS_1,CKV_AWS_3',
            '--skip-check', 'CKV_AWS_2,CKV_AWS_4',
            '-s',
            '--repo-id', 'abc',
            '-b', 'b/123',
        ])
        config = CheckovConfig.from_args(args)
        self.assertConfig({
            'source': 'args',
            'directory': {'/a1', '/b1', '/a2', '/b2'},
            'file': {'/a3', '/b3', '/a4', '/b4'},
            'external_checks_dir': {'/a5', '/b5'},
            'external_checks_git': {'/a6', '/b6'},
            '_output': 'json',
            'output': 'json',
            '_no_guide': True,
            'no_guide': True,
            '_quiet': True,
            'quiet': True,
            '_framework': 'kubernetes',
            'framework': 'kubernetes',
            'check': 'CKV_AWS_1,CKV_AWS_3',
            'skip_check': 'CKV_AWS_2,CKV_AWS_4',
            '_soft_fail': True,
            'soft_fail': True,
            'repo_id': 'abc',
            '_branch': 'b/123',
            'branch': 'b/123',
        }, config)

    def test_config_creation_long_args(self):
        parser = argparse.ArgumentParser()
        add_parser_args(parser)
        args = parser.parse_args([
            '--output', 'json',
            '--check', 'CKV_AWS_1,CKV_AWS_3',
            '--soft-fail',
            '--branch', 'b/123',
        ])
        config = CheckovConfig.from_args(args)
        self.assertConfig({
            'source': 'args',
            'directory': set(),
            'file': set(),
            'external_checks_dir': set(),
            'external_checks_git': set(),
            '_output': 'json',
            'output': 'json',
            '_no_guide': None,
            'no_guide': False,
            '_quiet': None,
            'quiet': False,
            '_framework': None,
            'framework': 'all',
            'check': 'CKV_AWS_1,CKV_AWS_3',
            'skip_check': None,
            '_soft_fail': True,
            'soft_fail': True,
            'repo_id': None,
            '_branch': 'b/123',
            'branch': 'b/123',
        }, config)
