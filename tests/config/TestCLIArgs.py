import unittest

from checkov.main import Checkov


class ConfigException(Exception):
    pass


# override parser.error, which prints the error and exits
def parser_error(message: str):
    raise ConfigException(message)


class TestCLIArgs(unittest.TestCase):
    def test_normalize_frameworks(self):
        argv = []
        ckv = Checkov(argv=argv)
        self.assertEqual(ckv.config.framework, ['all'])
        self.assertEqual(ckv.config.skip_framework, [])

        argv = ['--framework', 'terraform']
        ckv = Checkov(argv=argv)
        self.assertEqual(ckv.config.framework, ['terraform'])

        argv = ['--framework', 'terraform,arm']
        ckv = Checkov(argv=argv)
        self.assertEqual(set(ckv.config.framework), {'terraform', 'arm'})

        argv = ['--framework', 'terraform', 'arm']
        ckv = Checkov(argv=argv)
        self.assertEqual(set(ckv.config.framework), {'terraform', 'arm'})

        argv = ['--framework', 'terraform', '--framework', 'arm']
        ckv = Checkov(argv=argv)
        self.assertEqual(set(ckv.config.framework), {'terraform', 'arm'})

        argv = ['--framework', 'terraform,bicep', '--framework', 'arm']
        ckv = Checkov(argv=argv)
        self.assertEqual(set(ckv.config.framework), {'terraform', 'arm', 'bicep'})

        argv = ['--framework', 'terraform,bicep', '--framework', 'arm,all']
        ckv = Checkov(argv=argv)
        self.assertEqual(ckv.config.framework, ['all'])

        argv = ['--framework', 'terraform,bicep', '--framework', 'arm,invalid']
        ckv = Checkov(argv=[])  # first instantiate a valid one
        # now repeat some of the logic of the constructor, overriding values
        ckv.config = ckv.parser.parse_args(argv)
        ckv.parser.error = parser_error
        with self.assertRaises(ConfigException):
            ckv.normalize_config()

        # all is specified, so we do not expect an exception
        argv = ['--framework', 'terraform,bicep', '--framework', 'arm,invalid,all']
        ckv = Checkov(argv=argv)
        self.assertEqual(ckv.config.framework, ['all'])

    def test_normalize_skip_frameworks(self):
        argv = ['--skip-framework', 'terraform']
        ckv = Checkov(argv=argv)
        self.assertEqual(ckv.config.skip_framework, ['terraform'])

        argv = ['--skip-framework', 'terraform,arm']
        ckv = Checkov(argv=argv)
        self.assertEqual(set(ckv.config.skip_framework), {'terraform', 'arm'})

        argv = ['--skip-framework', 'terraform', 'arm']
        ckv = Checkov(argv=argv)
        self.assertEqual(set(ckv.config.skip_framework), {'terraform', 'arm'})

        argv = ['--skip-framework', 'terraform', '--skip-framework', 'arm']
        ckv = Checkov(argv=argv)
        self.assertEqual(set(ckv.config.skip_framework), {'terraform', 'arm'})

        argv = ['--skip-framework', 'terraform,bicep', '--skip-framework', 'arm']
        ckv = Checkov(argv=argv)
        self.assertEqual(set(ckv.config.skip_framework), {'terraform', 'arm', 'bicep'})

        # all is not allowed
        argv = ['--skip-framework', 'terraform,bicep', '--skip-framework', 'arm,all']
        ckv = Checkov(argv=[])
        ckv.config = ckv.parser.parse_args(argv)
        ckv.parser.error = parser_error
        with self.assertRaises(ConfigException):
            ckv.normalize_config()

        argv = ['--skip-framework', 'terraform,bicep', '--skip-framework', 'arm,invalid']
        ckv = Checkov(argv=[])
        ckv.config = ckv.parser.parse_args(argv)
        ckv.parser.error = parser_error
        with self.assertRaises(ConfigException):
            ckv.normalize_config()

    def test_combine_framework_and_skip(self):
        argv = ['--framework', 'terraform', '--skip-framework', 'arm']
        ckv = Checkov(argv=argv)
        self.assertEqual(ckv.config.framework, ['terraform'])
        self.assertEqual(ckv.config.skip_framework, ['arm'])

        # duplicate values not allowed
        argv = ['--framework', 'arm', '--skip-framework', 'arm']
        ckv = Checkov(argv=[])
        ckv.config = ckv.parser.parse_args(argv)
        ckv.parser.error = parser_error
        with self.assertRaises(ConfigException):
            ckv.normalize_config()

        # but it works with all
        argv = ['--framework', 'arm,all', '--skip-framework', 'arm']
        ckv = Checkov(argv=argv)
        self.assertEqual(ckv.config.framework, ['all'])
        self.assertEqual(ckv.config.skip_framework, ['arm'])

        # try using a non-standard tool name 
        argv = ['--tool-name', 'non_standard_name']
        ckv = Checkov(argv=argv)
        self.assertEqual(ckv.config.tool, ['non_standard_name'])

        # what about a standard tool name?
        argv = []
        ckv = Checkov(argv=argv)
        self.assertEqual(ckv.config.tool_name, ['checkov'])


if __name__ == '__main__':
    unittest.main()
