import os

import argparse
import itertools
from unittest.mock import patch, call

from checkov.config import CheckovConfig
from checkov.main import get_configuration_from_files, add_parser_args, get_configuration, \
    get_global_configuration_files, get_local_configuration_files
from tests.test_config import ConfigTestCase


def get_environment_with_home():
    res = dict(os.environ)
    if 'XDG_CONFIG_HOME' in res:
        del res['XDG_CONFIG_HOME']
    res['HOME'] = ''
    return res


# noinspection DuplicatedCode
class TestCheckovConfigConfigFileDetection(ConfigTestCase):
    local_paths = [
        'tox.ini',  # least important
        'setup.cfg',
        '.checkov.yml',
        '.checkov.yaml',
        '.checkov',  # most important
    ]

    full_file = '''---

directories:
  - /a
  - /b
  - c
  - "1"
files:
  - /a/m.tf
  - d.tf
external_checks_dirs:
  - /x
  - y
external_checks_gits:
  - a/b
  - c/d
output: json
no_guide: true
quiet: False
framework: kubernetes
merging_behavior: override
checks:
  - !!str 1
  - " a "
  - d
skip_checks:
  - "2"
  - " b "
  - "d"
soft_fail: TRUE
repo_id: 1 2
branch: feature/abc

'''
    full_config = CheckovConfig('file', directory={'/a', '/b', 'c', '1'}, file={'/a/m.tf', 'd.tf'},
                                external_checks_dir={'/x', 'y'}, external_checks_git={'a/b', 'c/d'}, output='json',
                                no_guide=True, quiet=False, framework='kubernetes', merging_behavior='override',
                                check='1, a ,d', skip_check='2, b ,d', soft_fail=True, repo_id='1 2',
                                branch='feature/abc')

    @patch.dict(os.environ, {'XDG_CONFIG_HOME': '/home/test_user/.config'})
    @patch('checkov.main.os_name', 'posix')
    def test_global_config_file_read_posix_if_xdg_config_home_is_set(self):
        files = get_global_configuration_files()
        # we set CDG_CONFIG_HOME to that value regardless if this is correct for the system. os.path.join will not
        # fix that. Therefore we use the same string here.
        expected = [os.path.join('/home/test_user/.config', 'checkov', 'config')]
        self.assertSequenceEqual(expected, list(files))

    @patch.dict(os.environ, {'HOME': '/home/use_1'})
    @patch('checkov.main.os_name', 'posix')
    def test_global_config_file_read_posix_if_home_is_set(self):
        if 'XDG_CONFIG_HOME' in os.environ:
            del os.environ['XDG_CONFIG_HOME']
        files = get_global_configuration_files()
        expected = [os.path.expanduser('~/.config/checkov/config')]
        self.assertSequenceEqual(expected, list(files))

    @patch.dict(os.environ, {'HOME': '/home/use_1'})
    @patch('checkov.main.os_name', 'nt')
    def test_global_config_file_read_nt_if_home_is_set(self):
        files = get_global_configuration_files()
        expected = [os.path.expanduser('~/.checkov/config')]
        self.assertSequenceEqual(expected, list(files))

    def test_local_config_file_read(self):
        files = get_local_configuration_files()
        self.assertSequenceEqual(self.local_paths, list(files))

    @patch('checkov.main.get_local_configuration_files')
    @patch('checkov.main.get_global_configuration_files')
    @patch('checkov.config.CheckovConfig.from_file')
    def test_get_configuration_from_files(self, from_file_mock, global_mock, local_mock):
        reed_files = {
            'local_tox.ini': CheckovConfig('local_tox.ini', merging_behavior='union', file={'b'},
                                           framework='terraform'),
            'local_setup.cfg': CheckovConfig('local_setup.cfg', merging_behavior='override_if_present', file={'c'}),
            'local_.checkov.yml': CheckovConfig('local_.checkov.yml', merging_behavior='copy_parent'),
            'local_.checkov.yaml': CheckovConfig('local_.checkov.yaml', merging_behavior='union', file={'d'},
                                                 branch='a'),
            'local_.checkov': CheckovConfig('local_.checkov', external_checks_dir={'a'}),
            'abc': CheckovConfig('abc', merging_behavior='union', external_checks_dir=['x']),
            'efg': CheckovConfig('efg', merging_behavior='override_if_present', file={'x'}),
        }
        default_reed_file = CheckovConfig('global', file={'a'}, framework='all', external_checks_dir={'tests'})

        def from_file_mock_impl(file):
            # Fall back to global config so the function will return a CheckovConfig. If the argument was wrong, this is
            # found later
            return reed_files.get(file, default_reed_file)

        from_file_mock.side_effect = from_file_mock_impl
        global_mock.return_value = global_mock_return_value = ['local_file.yaml']
        local_mock.return_value = local_mock_return_value = [
            'local_tox.ini',
            'local_setup.cfg',
            'local_.checkov.yml',
            'local_.checkov.yaml',
            'local_.checkov',
        ]

        expected = CheckovConfig('local_.checkov', file={'c', 'd'}, framework='terraform',
                                 external_checks_dir={'tests', 'a'}, branch='a')
        config = get_configuration_from_files()

        self.assertConfig(expected, config)
        local_mock.assert_called_once_with()
        global_mock.assert_called_once_with()
        from_file_calls = [
            call(path)
            for path in itertools.chain(global_mock_return_value, local_mock_return_value)
        ]
        from_file_mock.assert_has_calls(from_file_calls)
        self.assertEqual(from_file_mock.call_count, len(from_file_calls))

        from_file_mock.reset_mock()
        global_mock.reset_mock()
        local_mock.reset_mock()

        expected = CheckovConfig('efg', merging_behavior='override_if_present', file={'x'}, framework='terraform',
                                 external_checks_dir={'tests', 'a', 'x'}, branch='a')
        config = get_configuration_from_files(['abc', 'efg'])

        self.assertConfig(expected, config)
        local_mock.assert_called_once_with()
        global_mock.assert_called_once_with()
        from_file_calls = [
            call(path)
            for path in itertools.chain(global_mock_return_value, local_mock_return_value, ['abc', 'efg'])
        ]
        from_file_mock.assert_has_calls(from_file_calls)
        self.assertEqual(from_file_mock.call_count, len(from_file_calls))

    @patch('checkov.main.get_configuration_from_files')
    def test_get_configuration(self, get_configuration_from_files_mock):
        parser = argparse.ArgumentParser(description='Infrastructure as code static analysis')
        add_parser_args(parser)
        args = parser.parse_args([
            '--merging-behavior',
            'override',
        ])
        get_configuration_from_files_mock.return_value = CheckovConfig('file', file={'b'}, skip_check='')

        config = get_configuration(args)
        expected = CheckovConfig('args', merging_behavior='override')
        self.assertConfig(expected, config)
        get_configuration_from_files_mock.assert_called_once_with([])

    @patch('checkov.main.get_configuration_from_files')
    def test_get_configuration_with_additional_files(self, get_configuration_from_files_mock):
        parser = argparse.ArgumentParser(description='Infrastructure as code static analysis')
        add_parser_args(parser)
        args = parser.parse_args([
            '--merging-behavior',
            'override',
            '--config-files',
            'a',
            'b',
        ])
        get_configuration_from_files_mock.return_value = CheckovConfig('file', file={'b'}, skip_check='')

        config = get_configuration(args)
        expected = CheckovConfig('args', merging_behavior='override')
        self.assertConfig(expected, config)
        get_configuration_from_files_mock.assert_called_once_with(['a', 'b'])
