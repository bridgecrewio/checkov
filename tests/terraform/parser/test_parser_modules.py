import os
import shutil
import unittest
from pathlib import Path
from unittest import mock

import pytest

from checkov.common.util.consts import DEFAULT_EXTERNAL_MODULES_DIR
from checkov.common.util.parser_utils import TERRAFORM_NESTED_MODULE_PATH_PREFIX, TERRAFORM_NESTED_MODULE_PATH_ENDING, \
    TERRAFORM_NESTED_MODULE_INDEX_SEPARATOR
from checkov.terraform.parser import Parser


@pytest.fixture
def tmp_path(request, tmp_path: Path):
    # https://pytest.org/en/latest/how-to/unittest.html#mixing-pytest-fixtures-into-unittest-testcase-subclasses-using-marks
    request.cls.tmp_path = tmp_path


@pytest.mark.usefixtures("tmp_path")
class TestParserInternals(unittest.TestCase):

    def setUp(self) -> None:
        from checkov.terraform.module_loading.registry import ModuleLoaderRegistry

        # needs to be reset, because the cache belongs to the class not instance
        ModuleLoaderRegistry.module_content_cache = {}

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

    def test_load_inner_registry_module_with_nested_modules(self):
        parser = Parser()
        directory = os.path.join(self.resources_dir, "registry_security_group_inner_module")
        self.external_module_path = os.path.join(self.tmp_path, DEFAULT_EXTERNAL_MODULES_DIR)
        out_definitions = {}
        parser.parse_directory(directory=directory, out_definitions=out_definitions,
                               out_evaluations_context={},
                               download_external_modules=True,
                               external_modules_download_path=self.external_module_path)
        self.assertEqual(11, len(list(out_definitions.keys())))
        expected_remote_module_path = f'{self.external_module_path}/github.com/terraform-aws-modules/terraform-aws-security-group/v4.0.0'
        expected_inner_remote_module_path = f'{expected_remote_module_path}/modules/http-80'
        expected_main_file = os.path.join(directory, 'main.tf')
        expected_inner_main_file = os.path.join(directory, expected_inner_remote_module_path, 'main.tf')
        expected_file_names = [
            expected_main_file,
            os.path.join(directory, expected_inner_remote_module_path, f'auto_values.tf{TERRAFORM_NESTED_MODULE_PATH_PREFIX}{expected_main_file}{TERRAFORM_NESTED_MODULE_INDEX_SEPARATOR}0{TERRAFORM_NESTED_MODULE_PATH_ENDING}'),
            os.path.join(directory, expected_inner_remote_module_path, f'main.tf{TERRAFORM_NESTED_MODULE_PATH_PREFIX}{expected_main_file}{TERRAFORM_NESTED_MODULE_INDEX_SEPARATOR}0{TERRAFORM_NESTED_MODULE_PATH_ENDING}'),
            os.path.join(directory, expected_inner_remote_module_path, f'outputs.tf{TERRAFORM_NESTED_MODULE_PATH_PREFIX}{expected_main_file}{TERRAFORM_NESTED_MODULE_INDEX_SEPARATOR}0{TERRAFORM_NESTED_MODULE_PATH_ENDING}'),
            os.path.join(directory, expected_inner_remote_module_path, f'variables.tf{TERRAFORM_NESTED_MODULE_PATH_PREFIX}{expected_main_file}{TERRAFORM_NESTED_MODULE_INDEX_SEPARATOR}0{TERRAFORM_NESTED_MODULE_PATH_ENDING}'),
            os.path.join(directory, expected_inner_remote_module_path, f'versions.tf{TERRAFORM_NESTED_MODULE_PATH_PREFIX}{expected_main_file}{TERRAFORM_NESTED_MODULE_INDEX_SEPARATOR}0{TERRAFORM_NESTED_MODULE_PATH_ENDING}'),

            os.path.join(directory, expected_remote_module_path, f'main.tf{TERRAFORM_NESTED_MODULE_PATH_PREFIX}{expected_inner_main_file}{TERRAFORM_NESTED_MODULE_INDEX_SEPARATOR}0{TERRAFORM_NESTED_MODULE_PATH_ENDING}'),
            os.path.join(directory, expected_remote_module_path, f'outputs.tf{TERRAFORM_NESTED_MODULE_PATH_PREFIX}{expected_inner_main_file}{TERRAFORM_NESTED_MODULE_INDEX_SEPARATOR}0{TERRAFORM_NESTED_MODULE_PATH_ENDING}'),
            os.path.join(directory, expected_remote_module_path, f'rules.tf{TERRAFORM_NESTED_MODULE_PATH_PREFIX}{expected_inner_main_file}{TERRAFORM_NESTED_MODULE_INDEX_SEPARATOR}0{TERRAFORM_NESTED_MODULE_PATH_ENDING}'),
            os.path.join(directory, expected_remote_module_path, f'variables.tf{TERRAFORM_NESTED_MODULE_PATH_PREFIX}{expected_inner_main_file}{TERRAFORM_NESTED_MODULE_INDEX_SEPARATOR}0{TERRAFORM_NESTED_MODULE_PATH_ENDING}'),
            os.path.join(directory, expected_remote_module_path, f'versions.tf{TERRAFORM_NESTED_MODULE_PATH_PREFIX}{expected_inner_main_file}{TERRAFORM_NESTED_MODULE_INDEX_SEPARATOR}0{TERRAFORM_NESTED_MODULE_PATH_ENDING}'),
        ]

        for expected_file_name in expected_file_names:
            if not any(definition for definition in out_definitions.keys() if definition.startswith(expected_file_name[:-3])):
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

    def test_load_local_module(self):
        # given
        parser = Parser()
        directory = os.path.join(self.resources_dir, "local_module")
        out_definitions = {}

        # when
        parser.parse_directory(
            directory=directory, out_definitions=out_definitions, out_evaluations_context={}
        )

        # then
        self.assertEqual(len(out_definitions), 3)  # root file + 2x module file
        self.assertEqual(len(parser.loaded_files_map), 2)  # root file + 1x module file

    def test_load_nested_dup_module(self):
        parser = Parser()
        directory = os.path.join(self.resources_dir, "parser_dup_nested")
        out_definitions = {}
        parser.parse_directory(directory=directory, out_evaluations_context={}, out_definitions=out_definitions)

        self.assertEqual(len(out_definitions), 7)
        self.assertEqual(len(parser.loaded_files_map), 3)

    def test_load_local_nested_module(self):
        # given
        parser = Parser()
        directory = os.path.join(self.resources_dir, "parser_nested_modules")
        out_definitions = {}

        # when
        parser.parse_directory(
            directory=directory, out_definitions=out_definitions, out_evaluations_context={}
        )

        # then
        self.assertEqual(len(out_definitions), 5)  # root file + 2x module file
        self.assertEqual(len(parser.loaded_files_map), 5)  # root file + 1x module file
