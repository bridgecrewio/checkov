import os
import unittest

from checkov.cloudformation.context_parser import ContextParser
from checkov.cloudformation.runner import Runner
from checkov.runner_filter import RunnerFilter
from checkov.cloudformation.parser import parse


class TestCfnYaml(unittest.TestCase):

    def test_skip_parsing(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files = f'{current_dir}/skip.yaml'
        report = Runner().run(None, files=[test_files], runner_filter=RunnerFilter())
        summary = report.get_summary()

        self.assertEqual(summary['passed'], 2)
        self.assertEqual(summary['failed'], 3)
        self.assertEqual(summary['skipped'], 1)
        self.assertEqual(summary['parsing_errors'], 0)

    def test_code_line_extraction(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))

        # the test data that we'll evaluate against
        # line ranges are 1-based
        # mapping is file name, to resource index, to resource details
        # checking the resource index helps make sure that we are testing what we think we are testing
        files = [f'{current_dir}/cfn_newline_at_end.yaml', f'{current_dir}/cfn_nonewline_at_end.yaml']
        resource_properties_mapping = {
            files[0]: {
                0: {
                    'name': 'MyDB',
                    'line_range': [2, 9]
                },
                1: {
                    'name': 'MyBucket',
                    'line_range': [10, 13]
                }
            },
            files[1]: {
                0: {
                    'name': 'MyDB',
                    'line_range': [2, 9]
                },
                1: {
                    'name': 'MyBucket',
                    'line_range': [11, 14]
                }
            }
        }

        for file in files:
            cfn_dict, cfn_str = parse(file)

            cf_context_parser = ContextParser(file, cfn_dict, cfn_str)

            for index, (resource_name, resource) in enumerate(cfn_dict['Resources'].items()):
                # this filters out __startline__ and __endline__ markers
                resource_id = cf_context_parser.extract_cf_resource_id(resource, resource_name)
                if resource_id:
                    # make sure we are checking the right resource
                    self.assertEqual(resource_name, resource_properties_mapping[file][index]['name'])

                    entity_lines_range, entity_code_lines = cf_context_parser.extract_cf_resource_code_lines(resource)
                    self.assertEqual(entity_lines_range[0], entity_code_lines[0][0])
                    self.assertEqual(entity_lines_range[1], entity_code_lines[-1][0])
                    self.assertEqual(entity_lines_range, resource_properties_mapping[file][index]['line_range'])

    def test_trim_lines(self):
        # trim from front
        test1 = [
            (0, '\n'),
            (1, ''),
            (2, ' here is text'),
            (3, 'more text')
        ]

        self.assertEqual(ContextParser.trim_lines(test1), test1[2:4])

        # trim from back
        test2 = [
            (0, ' here is text'),
            (1, 'more text'),
            (2, '\n'),
            (3, ''),
        ]

        self.assertEqual(ContextParser.trim_lines(test2), test2[0:2])

        # trim from both
        test3 = [
            (0, '\n'),
            (1, ''),
            (2, ' here is text'),
            (3, 'more text'),
            (4, '\n'),
            (5, ''),
        ]

        self.assertEqual(ContextParser.trim_lines(test3), test3[2:4])

        # trim nothing
        test4 = [
            (2, ' here is text'),
            (3, 'more text'),
        ]

        self.assertEqual(ContextParser.trim_lines(test4), test4)

        # trim everything
        test5 = [
            (2, ''),
            (3, '\n'),
        ]

        self.assertEqual(ContextParser.trim_lines(test5), [])

    def test_parameter_import_lines(self):
        # check that when a parameter is imported into a resource, the line numbers of the resource are preserved
        current_dir = os.path.dirname(os.path.realpath(__file__))
        file = f'{current_dir}/cfn_with_ref.yaml'
        definitions, definitions_raw = parse(file)

        cf_context_parser = ContextParser(file, definitions, definitions_raw)
        resource = definitions['Resources']['ElasticsearchDomain']
        entity_lines_range, entity_code_lines = cf_context_parser.extract_cf_resource_code_lines(resource)
        self.assertEqual(entity_lines_range[0], 10)
        self.assertEqual(entity_lines_range[1], 20)

    def test_parsing_error(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files = ["cfn_bad_name.yaml", "cfn_with_ref_bad.yaml", "cfn_bad_iam.yaml"]
        report = Runner().run(None, files=[f'{current_dir}/{f}' for f in test_files], runner_filter=RunnerFilter())
        summary = report.get_summary()

        self.assertEqual(summary['passed'], 6)
        self.assertEqual(summary['failed'], 0)
        self.assertEqual(summary['skipped'], 0)
        self.assertEqual(summary['parsing_errors'], 2)


if __name__ == '__main__':
    unittest.main()
