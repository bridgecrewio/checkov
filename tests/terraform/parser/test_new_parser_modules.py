import os
import shutil
import unittest
from pathlib import Path

import pytest

from checkov.common.util.consts import DEFAULT_EXTERNAL_MODULES_DIR
from checkov.terraform import TFDefinitionKey, TFModule
from checkov.terraform.tf_parser import TFParser


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

        self.resources_dir = os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "./resources"))
        self.external_module_path = ''

    def tearDown(self) -> None:
        if os.path.exists(self.external_module_path):
            shutil.rmtree(self.external_module_path)

    def test_load_inner_registry_module_new_parser(self):
        parser = TFParser()
        directory = os.path.join(self.resources_dir, "registry_security_group_inner_module")
        self.external_module_path = os.path.join(self.tmp_path, DEFAULT_EXTERNAL_MODULES_DIR)
        out_definitions = parser.parse_directory(
            directory=directory,
            out_evaluations_context={},
            download_external_modules=True,
            external_modules_download_path=self.external_module_path)
        self.assertEqual(11, len(list(out_definitions.keys())))
        expected_remote_module_path = f'{self.external_module_path}/github.com/terraform-aws-modules/terraform-aws-security-group/v4.0.0'
        expected_inner_remote_module_path = f'{expected_remote_module_path}/modules/http-80'
        expected_main_file = os.path.join(directory, 'main.tf')

        assert TFDefinitionKey(file_path=expected_main_file) in out_definitions

        assert TFDefinitionKey(file_path=f"{expected_inner_remote_module_path}/auto_values.tf", tf_source_modules=TFModule(name='web_server_sg', path=expected_main_file)) in out_definitions
        assert TFDefinitionKey(file_path=f"{expected_inner_remote_module_path}/main.tf", tf_source_modules=TFModule(name='web_server_sg', path=expected_main_file)) in out_definitions
        assert TFDefinitionKey(file_path=f"{expected_inner_remote_module_path}/outputs.tf", tf_source_modules=TFModule(name='web_server_sg', path=expected_main_file)) in out_definitions
        assert TFDefinitionKey(file_path=f"{expected_inner_remote_module_path}/variables.tf", tf_source_modules=TFModule(name='web_server_sg', path=expected_main_file)) in out_definitions
        assert TFDefinitionKey(file_path=f"{expected_inner_remote_module_path}/versions.tf", tf_source_modules=TFModule(name='web_server_sg', path=expected_main_file)) in out_definitions

        assert TFDefinitionKey(file_path=f"{expected_remote_module_path}/main.tf", tf_source_modules=TFModule(name='sg', path=f"{expected_inner_remote_module_path}/main.tf", nested_tf_module=TFModule(path=expected_main_file, name='web_server_sg'))) in out_definitions
        assert TFDefinitionKey(file_path=f"{expected_remote_module_path}/outputs.tf", tf_source_modules=TFModule(name='sg', path=f"{expected_inner_remote_module_path}/main.tf", nested_tf_module=TFModule(path=expected_main_file, name='web_server_sg'))) in out_definitions
        assert TFDefinitionKey(file_path=f"{expected_remote_module_path}/rules.tf", tf_source_modules=TFModule(name='sg', path=f"{expected_inner_remote_module_path}/main.tf", nested_tf_module=TFModule(path=expected_main_file, name='web_server_sg'))) in out_definitions
        assert TFDefinitionKey(file_path=f"{expected_remote_module_path}/variables.tf", tf_source_modules=TFModule(name='sg', path=f"{expected_inner_remote_module_path}/main.tf", nested_tf_module=TFModule(path=expected_main_file, name='web_server_sg'))) in out_definitions
        assert TFDefinitionKey(file_path=f"{expected_remote_module_path}/versions.tf", tf_source_modules=TFModule(name='sg', path=f"{expected_inner_remote_module_path}/main.tf", nested_tf_module=TFModule(path=expected_main_file, name='web_server_sg'))) in out_definitions

    def test_invalid_module_sources_new_parser(self):
        parser = TFParser()
        directory = os.path.join(self.resources_dir, "failing_module_address")
        self.external_module_path = os.path.join(directory, DEFAULT_EXTERNAL_MODULES_DIR)
        out_definitions = parser.parse_directory(
            directory=directory,
            out_evaluations_context={},
            download_external_modules=True,
            external_modules_download_path=DEFAULT_EXTERNAL_MODULES_DIR)
        # check that only the original file was parsed successfully without getting bad external modules
        self.assertEqual(1, len(list(out_definitions.keys())))

    def test_malformed_output_blocks_new_parser(self):
        parser = TFParser()
        directory = os.path.join(self.resources_dir, "malformed_outputs")
        self.external_module_path = os.path.join(directory, DEFAULT_EXTERNAL_MODULES_DIR)
        out_definitions = parser.parse_directory(
            directory=directory,
            out_evaluations_context={},
            download_external_modules=True,
            external_modules_download_path=DEFAULT_EXTERNAL_MODULES_DIR)
        file_path, entity_definitions = next(iter(out_definitions.items()))
        self.assertEqual(2, len(list(out_definitions[file_path]['output'])))

    def test_load_local_module_new_parser(self):
        parser = TFParser()
        directory = os.path.join(self.resources_dir, "local_module")
        out_definitions = parser.parse_directory(directory=directory, out_evaluations_context={})

        self.assertEqual(len(out_definitions), 3)
        self.assertEqual(len(parser.loaded_files_map), 2)

        local_module_path = os.path.join(directory, 'main.tf')
        module_path = os.path.join(directory, "module/main.tf")
        main_key = TFDefinitionKey(file_path=local_module_path)
        key_idx_0 = TFDefinitionKey(file_path=module_path, tf_source_modules=TFModule(path=local_module_path, name='mod'))
        key_idx_1 = TFDefinitionKey(file_path=module_path, tf_source_modules=TFModule(path=local_module_path, name='mod2'))

        assert main_key in out_definitions
        assert key_idx_0 in out_definitions
        assert key_idx_1 in out_definitions
        assert out_definitions[main_key]['module'][0]['mod']['__resolved__'] == [key_idx_0]
        assert out_definitions[main_key]['module'][1]['mod2']['__resolved__'] == [key_idx_1]

        assert parser.external_modules_source_map == {(os.path.join(directory, 'module'), 'latest'): os.path.join(directory, 'module')}
        assert parser.external_variables_data == [
            ('versioning', True, 'manual specification'),
            ('__start_line__', 1, 'manual specification'),
            ('__end_line__', 4, 'manual specification'),
            ('versioning', False, 'manual specification'),
            ('__start_line__', 6, 'manual specification'),
            ('__end_line__', 9, 'manual specification')
        ]
        assert parser.keys_to_remove == {TFDefinitionKey(file_path=module_path)}
        assert parser._parsed_directories == {
            directory,
            os.path.join(directory, 'module')
        }

    def test_load_nested_module_new_parser(self):
        parser = TFParser()
        directory = os.path.join(self.resources_dir, "parser_nested_modules")
        o_definitions = parser.parse_directory(directory=directory, out_evaluations_context={})

        self.assertEqual(len(o_definitions), 5)
        self.assertEqual(len(parser.loaded_files_map), 5)

        main_module_path = os.path.join(directory, 'main.tf')
        module2_main_path = os.path.join(directory, 'module/module2/main.tf')
        module2_var_path = os.path.join(directory, 'module/module2/variable.tf')
        module1_main_path = os.path.join(directory, 'module/main.tf')
        module1_var_path = os.path.join(directory, 'module/variable.tf')

        main_module = TFDefinitionKey(file_path=main_module_path)
        module_main_key = TFDefinitionKey(file_path=module1_main_path, tf_source_modules=TFModule(path=main_module_path, name='s3_module'))
        module_var_key = TFDefinitionKey(file_path=module1_var_path, tf_source_modules=TFModule(path=main_module_path, name='s3_module'))
        module2_main_key = TFDefinitionKey(file_path=module2_main_path, tf_source_modules=TFModule(path=module1_main_path, name='inner_s3_module', nested_tf_module=TFModule(path=main_module_path, name='s3_module')))
        module2_var_key = TFDefinitionKey(file_path=module2_var_path, tf_source_modules=TFModule(path=module1_main_path, name='inner_s3_module', nested_tf_module=TFModule(path=main_module_path, name='s3_module')))

        assert main_module in o_definitions
        assert module_main_key in o_definitions
        assert module_var_key in o_definitions
        assert module2_main_key in o_definitions
        assert module2_var_key in o_definitions

        assert o_definitions[main_module]['module'][0]['s3_module']['__resolved__'] == [module_main_key, module_var_key]
        assert o_definitions[module_main_key]['module'][0]['inner_s3_module']['__resolved__'] == [module2_main_key, module2_var_key]

    def test_load_nested_dup_module(self):
        parser = TFParser()
        directory = os.path.join(self.resources_dir, "parser_dup_nested")
        o_definitions = parser.parse_directory(directory=directory, out_evaluations_context={})

        self.assertEqual(len(o_definitions), 7)
        self.assertEqual(len(parser.loaded_files_map), 3)

        main_module_path = os.path.join(directory, 'main.tf')
        module1_path = os.path.join(directory, 'module/main.tf')
        module2_path = os.path.join(directory, 'module/module2/main.tf')

        main_module = TFDefinitionKey(file_path=main_module_path)
        module1_key0 = TFDefinitionKey(file_path=module1_path, tf_source_modules=TFModule(path=main_module_path, name='s3_module'))
        module1_key1 = TFDefinitionKey(file_path=module1_path, tf_source_modules=TFModule(path=main_module_path, name='s3_module2'))
        module2_key0_nest0 = TFDefinitionKey(file_path=module2_path, tf_source_modules=TFModule(path=module1_path, name='inner_s3_module', nested_tf_module=TFModule(path=main_module_path, name='s3_module')))
        module2_key1_nest0 = TFDefinitionKey(file_path=module2_path, tf_source_modules=TFModule(path=module1_path, name='inner_s3_module2', nested_tf_module=TFModule(path=main_module_path, name='s3_module')))
        module2_key0_nest1 = TFDefinitionKey(file_path=module2_path, tf_source_modules=TFModule(path=module1_path, name='inner_s3_module', nested_tf_module=TFModule(path=main_module_path, name='s3_module2')))
        module2_key1_nest1 = TFDefinitionKey(file_path=module2_path, tf_source_modules=TFModule(path=module1_path, name='inner_s3_module2', nested_tf_module=TFModule(path=main_module_path, name='s3_module2')))

        assert main_module in o_definitions
        assert module1_key0 in o_definitions
        assert module1_key1 in o_definitions
        assert module2_key0_nest1 in o_definitions
        assert module2_key1_nest1 in o_definitions
        assert module2_key0_nest0 in o_definitions
        assert module2_key1_nest0 in o_definitions
