import unittest
import configargparse

from checkov.common.util.ext_argument_parser import ExtArgumentParser


class TestConfigFile(unittest.TestCase):
    def test_pass(self):
        argv = ['--ca-certificate', '----- BEGIN CERTIFICATE ----- <KEY> ----- END CERTIFICATE -----',
                '--compact', '--directory', 'test-dir', '--docker-image', 'sample-image', '--dockerfile-path',
                'Dockerfile', '--download-external-modules', 'True', '--evaluate-variables', 'False',
                '--external-checks-dir', 'sample-dir', '--external-checks-git', 'sample-github-url', '--file',
                'sample.tf', '--framework', 'all', '--output', 'cli', '--quiet', '--repo-id',
                'bridgecrew/sample-repo', '--skip-check', 'CKV_DOCKER_3,CKV_DOCKER_2',
                '--skip-framework', 'dockerfile', '--soft-fail', '--branch', 'master',
                '--check', 'CKV_DOCKER_1']
        argv_parser = ExtArgumentParser(config_file_parser_class=configargparse.YAMLConfigFileParser)
        config_parser = ExtArgumentParser(
            config_file_parser_class=configargparse.YAMLConfigFileParser,
            default_config_files=['example_TestConfigFile/config.yml'],
        )

        argv_parser.add_parser_args()
        config_parser.add_parser_args()

        config_from_argv = argv_parser.parse_args(argv)
        config_from_file = config_parser.parse_args([])
        self.assertEqual(config_from_argv, config_from_file)


if __name__ == '__main__':
    unittest.main()
