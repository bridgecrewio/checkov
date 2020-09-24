import os

from unittest.mock import patch, mock_open, call

from checkov.config import CheckovConfig
from checkov.main import get_configuration_from_global_files, get_configuration_from_local_files, \
    get_configuration_from_files
from tests.test_config import ConfigTestCase


def get_environment_with_home():
    res = dict(os.environ)
    if 'XDG_CONFIG_HOME' in res:
        del res['XDG_CONFIG_HOME']
    res['HOME'] = ''
    return res


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
        with patch('builtins.open', mock_open(read_data=self.full_file)) as mock_file:
            config = get_configuration_from_global_files()
            self.assertConfig(self.full_config, config)
            # we set CDG_CONFIG_HOME to that value regardless if this is correct for the system. os.path.join will not
            # fix that. Therefore we use the same string here.
            mock_file.assert_called_once_with(os.path.join('/home/test_user/.config', 'checkov', 'config'), 'r')

    @patch.dict(os.environ, {'XDG_CONFIG_HOME': '/home/test_user/.config'})
    @patch('checkov.main.os_name', 'posix')
    @patch('builtins.open')
    def test_global_config_file_read_posix_if_xdg_config_home_is_set_error(self, mock_file):
        mock_file.side_effect = OSError
        config = get_configuration_from_global_files()
        self.assertIsNone(config)
        # we set CDG_CONFIG_HOME to that value regardless if this is correct for the system. os.path.join will not
        # fix that. Therefore we use the same string here.
        mock_file.assert_called_once_with(os.path.join('/home/test_user/.config', 'checkov', 'config'), 'r')

    @patch.dict(os.environ, {'HOME': '/home/use_1'})
    @patch('checkov.main.os_name', 'posix')
    def test_global_config_file_read_posix_if_home_is_set(self):
        if 'XDG_CONFIG_HOME' in os.environ:
            del os.environ['XDG_CONFIG_HOME']
        with patch('builtins.open', mock_open(read_data=self.full_file)) as mock_file:
            config = get_configuration_from_global_files()
            self.assertConfig(self.full_config, config)
            mock_file.assert_called_once_with(os.path.expanduser('~/.config/checkov/config'), 'r')

    @patch.dict(os.environ, {'HOME': '/home/use_1'})
    @patch('checkov.main.os_name', 'posix')
    @patch('builtins.open')
    def test_global_config_file_read_posix_if_home_is_set_error(self, mock_file):
        if 'XDG_CONFIG_HOME' in os.environ:
            del os.environ['XDG_CONFIG_HOME']
        mock_file.side_effect = OSError
        config = get_configuration_from_global_files()
        self.assertIsNone(config)
        mock_file.assert_called_once_with(os.path.expanduser('~/.config/checkov/config'), 'r')

    @patch.dict(os.environ, {'HOME': '/home/use_1'})
    @patch('checkov.main.os_name', 'nt')
    def test_global_config_file_read_nt_if_home_is_set(self):
        with patch('builtins.open', mock_open(read_data=self.full_file)) as mock_file:
            config = get_configuration_from_global_files()
            self.assertConfig(self.full_config, config)
            mock_file.assert_called_once_with(os.path.expanduser('~/.checkov/config'), 'r')

    @patch.dict(os.environ, {'HOME': '/home/use_1'})
    @patch('checkov.main.os_name', 'nt')
    @patch('builtins.open')
    def test_global_config_file_read_nt_if_home_is_set_error(self, mock_file):
        mock_file.side_effect = OSError
        if 'XDG_CONFIG_HOME' in os.environ:
            del os.environ['XDG_CONFIG_HOME']
        config = get_configuration_from_global_files()
        self.assertIsNone(config)
        mock_file.assert_called_once_with(os.path.expanduser('~/.checkov/config'), 'r')

    def test_local_config_file_read(self):
        with patch('builtins.open', mock_open(read_data=self.full_file)) as mock_file:
            configs = get_configuration_from_local_files()
            for path, config in zip(self.local_paths, configs):
                self.assertConfig(self.full_config, config)
                mock_file.assert_called_with(path, 'r')
            with self.assertRaises(StopIteration, msg='Got more config files then expected'):
                next(configs)
            self.assertEqual(len(self.local_paths), mock_file.call_count,
                             f'Got fewer ({mock_file.call_count}) files then expected ({len(self.local_paths)})')

    @patch('builtins.open')
    def test_local_config_file_read_error(self, mock_file):
        mock_file.side_effect = OSError
        configs = get_configuration_from_local_files()
        with self.assertRaises(StopIteration, msg='No config could be read so the iterator is empty'):
            next(configs)
        mock_file.assert_has_calls([call(path, 'r') for path in self.local_paths])
        self.assertEqual(len(self.local_paths), mock_file.call_count,
                         f'Got fewer ({mock_file.call_count}) files then expected ({len(self.local_paths)})')

    @patch('checkov.main.get_configuration_from_local_files')
    @patch('checkov.main.get_configuration_from_global_files')
    def test_get_configuration_from_files(self, global_mock, local_mock):
        global_mock.return_value = CheckovConfig('global', file={'a'}, framework='all', external_checks_dir={'tests'})
        local_configs = [
            CheckovConfig('local_tox.ini', merging_behavior='union', file={'b'}, framework='terraform'),
            CheckovConfig('local_setup.cfg', merging_behavior='override_if_present', file={'c'}),
            CheckovConfig('local_.checkov.yml', merging_behavior='copy_parent'),
            CheckovConfig('local_.checkov.yaml', merging_behavior='union', file={'d'}, branch='a'),
            CheckovConfig('local_.checkov', external_checks_dir={'a'}),
        ]

        expected = CheckovConfig('local_.checkov', file={'c', 'd'}, framework='terraform',
                                 external_checks_dir={'tests', 'a'}, branch='a')
        self.assertEqual(len(self.local_paths), len(local_configs),
                         'Update this test. The amount of checks is not valid')
        local_mock.return_value = local_configs
        config = get_configuration_from_files()
        self.assertConfig(expected, config)
        global_mock.assert_called_once_with()
        local_mock.assert_called_once_with()
