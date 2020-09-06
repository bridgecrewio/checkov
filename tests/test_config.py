import unittest

import argparse
from typing import Union

from checkov.config import CheckovConfig
from checkov.main import add_parser_args


class TestCheckovConfig(unittest.TestCase):
    def assertCheckSkipCheckIsValid(self, config: CheckovConfig, msg=None):
        if msg:
            msg = msg + ': '
        self.assertFalse(config.check and config.skip_check,
                         f'{msg}Expected non or only one of check and skip_check to have a value set')

    def assertCheckSkipCheckIsInvalid(self, config: CheckovConfig, msg=None):
        if msg:
            msg = msg + ': '
        self.assertTrue(config.check, f'{msg}Expected check to be set. bot was "{config.check}"')
        self.assertTrue(config.skip_check, f'{msg}Expected skip_check to be set. bot was "{config.skip_check}"')

    def assertConfig(self, expected: Union[dict, CheckovConfig], config: CheckovConfig, msg_prefix=''):
        if isinstance(expected, CheckovConfig):
            class Wrapper:
                __slots__ = ['config']

                def __init__(self, c):
                    self.config = c

                def __getitem__(self, item):
                    return getattr(self.config, item)

            expected = Wrapper(expected)
        if msg_prefix:
            msg_prefix = msg_prefix + ': '
        self.assertEqual(expected['source'], config.source,
                         f'{msg_prefix}Expect source to be "{expected["source"]}" but got "{config.source}"')
        self.assertIsInstance(config.directory, frozenset,
                              f'{msg_prefix}Expect directory to be a set but got "{type(config.directory)}"')
        self.assertSetEqual(expected['directory'], config.directory,
                            f'{msg_prefix}Expect directory to be "{expected["directory"]}" but got '
                            f'"{config.directory}"')
        self.assertIsInstance(config.file, frozenset,
                              f'{msg_prefix}Expect file to be a set but got "{type(config.file)}"')
        self.assertSetEqual(expected['file'], config.file,
                            f'{msg_prefix}Expect file to be "{expected["file"]}" but got "{config.file}"')
        self.assertIsInstance(config.external_checks_dir, frozenset,
                              f'{msg_prefix}Expect external_checks_dir to be a set but got '
                              f'"{type(config.external_checks_dir)}"')
        self.assertSetEqual(expected['external_checks_dir'], config.external_checks_dir,
                            f'{msg_prefix}Expect external_checks_dir to be "{expected["external_checks_dir"]}" but '
                            f'got "{config.external_checks_dir}"')
        self.assertIsInstance(config.external_checks_git, frozenset,
                              f'{msg_prefix}Expect external_checks_git to be a set but got '
                              f'"{type(config.external_checks_git)}"')
        self.assertSetEqual(expected['external_checks_git'], config.external_checks_git,
                            f'{msg_prefix}Expect external_checks_git to be "{expected["external_checks_git"]}" but '
                            f'got "{config.external_checks_git}"')
        self.assertEqual(expected['_output'], config._output,
                         f'{msg_prefix}Expect _output to be "{expected["_output"]}" but got "{config._output}"')
        self.assertEqual(expected['output'], config.output,
                         f'{msg_prefix}Expect output to be "{expected["output"]}" but got "{config.output}"')
        self.assertEqual(expected['_no_guide'], config._no_guide,
                         f'{msg_prefix}Expect _no_guide to be "{expected["_no_guide"]}" but got "{config._no_guide}"')
        self.assertEqual(expected['no_guide'], config.no_guide,
                         f'{msg_prefix}Expect no_guide to be "{expected["no_guide"]}" but got "{config.no_guide}"')
        self.assertEqual(expected['_quiet'], config._quiet,
                         f'{msg_prefix}Expect _quiet to be "{expected["_quiet"]}" but got "{config._quiet}"')
        self.assertEqual(expected['quiet'], config.quiet,
                         f'{msg_prefix}Expect quiet to be "{expected["quiet"]}" but got "{config.quiet}"')
        self.assertEqual(expected['_framework'], config._framework,
                         f'{msg_prefix}Expect _framework to be "{expected["_framework"]}" but got '
                         f'"{config._framework}"')
        self.assertEqual(expected['framework'], config.framework,
                         f'{msg_prefix}Expect framework to be "{expected["framework"]}" but got "{config.framework}"')
        self.assertEqual(expected['check'], config.check,
                         f'{msg_prefix}Expect check to be "{expected["check"]}" but got "{config.check}"')
        self.assertEqual(expected['skip_check'], config.skip_check,
                         f'{msg_prefix}Expect skip_check to be "{expected["skip_check"]}" but got '
                         f'"{config.skip_check}"')
        self.assertEqual(expected['_soft_fail'], config._soft_fail,
                         f'{msg_prefix}Expect _soft_fail to be "{expected["_soft_fail"]}" but got '
                         f'"{config._soft_fail}"')
        self.assertEqual(expected['soft_fail'], config.soft_fail,
                         f'{msg_prefix}Expect soft_fail to be "{expected["soft_fail"]}" but got "{config.soft_fail}"')
        self.assertEqual(expected['repo_id'], config.repo_id,
                         f'{msg_prefix}Expect repo_id to be "{expected["repo_id"]}" but got "{config.repo_id}"')
        self.assertEqual(expected['_branch'], config._branch,
                         f'{msg_prefix}Expect _branch to be "{expected["_branch"]}" but got "{config._branch}"')
        self.assertEqual(expected['branch'], config.branch,
                         f'{msg_prefix}Expect branch to be "{expected["branch"]}" but got "{config.branch}"')

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

    def test_merge_config_no_override_if_defined(self):
        config1 = CheckovConfig('test')
        parent1 = CheckovConfig('test', directory={'1', '2'}, check='CKV_AWS_1,CKV_AWS_10', soft_fail=True, quiet=False)
        config1.extend(parent1)
        self.assertConfig(parent1, config1)

        config2 = CheckovConfig('test')
        parent2 = CheckovConfig('test', no_guide=True, framework='terraform', repo_id='123', branch='456', check='3,4')
        config2.extend(parent2)
        self.assertConfig(parent2, config2)

    def test_merge_does_not_change_parent(self):
        config = CheckovConfig('test')
        parent = CheckovConfig('p2', no_guide=True, framework='terraform', repo_id='123', branch='456', check='3,4')
        parent_clone = CheckovConfig('p2', no_guide=True, framework='terraform', repo_id='123', branch='456',
                                     check='3,4')
        config.extend(parent)
        self.assertConfig(parent_clone, parent, 'Parent should not be modified')

    def test_merge_sets_are_combined(self):
        child = CheckovConfig('test_child', directory={'a', 'b', 'c'}, file={'g', 'h', 'i'},
                              external_checks_dir={'m', 'n', 'o'}, external_checks_git={'s', 't', 'u'})
        parent = CheckovConfig('test_parent', directory={'c', 'd', 'e'}, file={'i', 'j', 'k'},
                               external_checks_dir={'o', 'p', 'q'}, external_checks_git={'u', 'v', 'w'})
        expected = CheckovConfig('test_child', directory={'a', 'b', 'c', 'd', 'e'}, file={'g', 'h', 'i', 'j', 'k'},
                                 external_checks_dir={'m', 'n', 'o', 'p', 'q'},
                                 external_checks_git={'s', 't', 'u', 'v', 'w'})
        child.extend(parent)
        self.assertConfig(expected, child)

    def test_merge_set_boolean_not_overridden(self):
        child_true = CheckovConfig('test_child', no_guide=True, quiet=True, soft_fail=True)
        child_true_clone = CheckovConfig('test_child', no_guide=True, quiet=True, soft_fail=True)
        child_false = CheckovConfig('test_child', no_guide=False, quiet=False, soft_fail=False)
        child_false_clone = CheckovConfig('test_child', no_guide=False, quiet=False, soft_fail=False)

        parents = [
            CheckovConfig('', no_guide=True, quiet=False, soft_fail=False),
            CheckovConfig('', no_guide=False, quiet=True, soft_fail=True),
            CheckovConfig(''),
            CheckovConfig('', no_guide=False),
            CheckovConfig('', soft_fail=True),
        ]

        self.assertConfig(child_true_clone, child_true)
        self.assertConfig(child_false_clone, child_false)
        for parent in parents:
            child_true.extend(parent)
            child_false.extend(parent)
            self.assertConfig(child_true_clone, child_true)
            self.assertConfig(child_false_clone, child_false)

    def test_merge_check_skip_check_merging_check_set(self):
        child = CheckovConfig('test', check='1')
        self.assertCheckSkipCheckIsValid(child)
        self.assertConfig(CheckovConfig('test', check='1'), child)
        child.extend(CheckovConfig('test'))
        self.assertCheckSkipCheckIsValid(child)
        self.assertConfig(CheckovConfig('test', check='1'), child)
        child.extend(CheckovConfig('test', skip_check='D,5'))
        self.assertCheckSkipCheckIsValid(child)
        self.assertConfig(CheckovConfig('test', check='1'), child)
        child.extend(CheckovConfig('test', check='D,9'))
        self.assertCheckSkipCheckIsValid(child)
        self.assertConfig(CheckovConfig('test', check='1,D,9'), child)
        child.extend(CheckovConfig('test', check='123,4,2', skip_check='D,5'))
        self.assertCheckSkipCheckIsValid(child)
        self.assertConfig(CheckovConfig('test', check='1,D,9,123,4,2'), child)

    def test_merge_check_skip_check_merging_skip_check_set(self):
        child = CheckovConfig('test', skip_check='2')
        self.assertCheckSkipCheckIsValid(child)
        self.assertConfig(CheckovConfig('test', skip_check='2'), child)
        child.extend(CheckovConfig('test', check='KL,asd'))
        self.assertCheckSkipCheckIsValid(child)
        self.assertConfig(CheckovConfig('test', skip_check='2'), child)
        child.extend(CheckovConfig('test'))
        self.assertCheckSkipCheckIsValid(child)
        self.assertConfig(CheckovConfig('test', skip_check='2'), child)
        child.extend(CheckovConfig('test', skip_check='D,5'))
        self.assertCheckSkipCheckIsValid(child)
        self.assertConfig(CheckovConfig('test', skip_check='2,D,5'), child)
        child.extend(CheckovConfig('test', check='123', skip_check='K'))
        self.assertCheckSkipCheckIsValid(child)
        self.assertConfig(CheckovConfig('test', skip_check='2,D,5,K'), child)

    def test_merge_invalid_check_skip_check_constellation(self):
        child = CheckovConfig('test', check='1', skip_check='2')
        self.assertCheckSkipCheckIsInvalid(child)
        child.extend(CheckovConfig('test'))
        self.assertCheckSkipCheckIsInvalid(child)
        child.extend(CheckovConfig('test', check='2'))
        self.assertCheckSkipCheckIsInvalid(child)
        child.extend(CheckovConfig('test', skip_check='D,5'))
        self.assertCheckSkipCheckIsInvalid(child)
        child.extend(CheckovConfig('test', check='123', skip_check='D,5'))
        self.assertCheckSkipCheckIsInvalid(child)

    def test_merge_copy_from_parent_if_not_set(self):
        child = CheckovConfig('t1')
        parent = CheckovConfig('t2', check='1', skip_check='2')
        child.extend(parent)
        expected = CheckovConfig('t1', check='1', skip_check='2')
        self.assertConfig(expected, child)
