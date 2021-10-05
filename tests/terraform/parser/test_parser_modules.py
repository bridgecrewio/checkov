import os
import shutil
import unittest

from checkov.common.util.consts import DEFAULT_EXTERNAL_MODULES_DIR
from checkov.terraform.parser import Parser


class TestParserInternals(unittest.TestCase):

    def setUp(self) -> None:
        self.resources_dir = os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                           "./resources"))
        self.external_module_path = ''

    def tearDown(self) -> None:
        if os.path.exists(self.external_module_path):
            shutil.rmtree(self.external_module_path)

    def test_load_registry_module(self):
        parser = Parser()
        directory = os.path.join(self.resources_dir, "registry_security_group")
        self.external_module_path = os.path.join(directory, DEFAULT_EXTERNAL_MODULES_DIR)
        out_definitions = {}
        parser.parse_directory(directory=directory, out_definitions=out_definitions,
                               out_evaluations_context={},
                               download_external_modules=True,
                               external_modules_download_path=DEFAULT_EXTERNAL_MODULES_DIR)

        external_aws_modules_path = os.path.join(self.external_module_path, 'github.com/terraform-aws-modules/terraform-aws-security-group/v3.18.0')
        assert os.path.exists(external_aws_modules_path)

    def test_load_inner_registry_module(self):
        parser = Parser()
        directory = os.path.join(self.resources_dir, "registry_security_group_inner_module")
        self.external_module_path = os.path.join(directory, DEFAULT_EXTERNAL_MODULES_DIR)
        out_definitions = {}
        parser.parse_directory(directory=directory, out_definitions=out_definitions,
                               out_evaluations_context={},
                               download_external_modules=True,
                               external_modules_download_path=DEFAULT_EXTERNAL_MODULES_DIR)
        self.assertEqual(11, len(list(out_definitions.keys())))
        expected_remote_module_path = f'{DEFAULT_EXTERNAL_MODULES_DIR}/github.com/terraform-aws-modules/terraform-aws-security-group/v4.0.0'
        expected_inner_remote_module_path = f'{expected_remote_module_path}/modules/http-80'
        expected_main_file = os.path.join(directory, 'main.tf')
        expected_inner_main_file = os.path.join(directory, expected_inner_remote_module_path, 'main.tf')
        expected_file_names = [
            expected_main_file,
            os.path.join(directory, expected_inner_remote_module_path, f'auto_values.tf[{expected_main_file}#0]'),
            os.path.join(directory, expected_inner_remote_module_path, f'main.tf[{expected_main_file}#0]'),
            os.path.join(directory, expected_inner_remote_module_path, f'outputs.tf[{expected_main_file}#0]'),
            os.path.join(directory, expected_inner_remote_module_path, f'variables.tf[{expected_main_file}#0]'),
            os.path.join(directory, expected_inner_remote_module_path, f'versions.tf[{expected_main_file}#0]'),

            os.path.join(directory, expected_remote_module_path, f'main.tf[{expected_inner_main_file}#0]'),
            os.path.join(directory, expected_remote_module_path, f'outputs.tf[{expected_inner_main_file}#0]'),
            os.path.join(directory, expected_remote_module_path, f'rules.tf[{expected_inner_main_file}#0]'),
            os.path.join(directory, expected_remote_module_path, f'variables.tf[{expected_inner_main_file}#0]'),
            os.path.join(directory, expected_remote_module_path, f'versions.tf[{expected_inner_main_file}#0]'),
        ]

        for expected_file_name in expected_file_names:
            if expected_file_name not in list(out_definitions.keys()):
                self.fail(f"expected file {expected_file_name} to be in out_definitions")

    def test_invalid_module_sources(self):
        parser = Parser()
        directory = os.path.join(self.resources_dir, "failing_module_address")
        self.external_module_path = os.path.join(directory, DEFAULT_EXTERNAL_MODULES_DIR)
        out_definitions = {}
        parser.parse_directory(directory=directory, out_definitions=out_definitions,
                               out_evaluations_context={},
                               download_external_modules=True,
                               external_modules_download_path=DEFAULT_EXTERNAL_MODULES_DIR)
        # check that only the original file was parsed successfully without getting bad external modules
        self.assertEqual(1, len(list(out_definitions.keys())))

    def test_malformed_output_blocks(self):
        parser = Parser()
        directory = os.path.join(self.resources_dir, "malformed_outputs")
        self.external_module_path = os.path.join(directory, DEFAULT_EXTERNAL_MODULES_DIR)
        out_definitions = {}
        parser.parse_directory(directory=directory, out_definitions=out_definitions,
                               out_evaluations_context={},
                               download_external_modules=True,
                               external_modules_download_path=DEFAULT_EXTERNAL_MODULES_DIR)
        file_path, entity_definitions = next(iter(out_definitions.items()))
        self.assertEqual(2, len(list(out_definitions[file_path]['output'])))
