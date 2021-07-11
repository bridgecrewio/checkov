import json
import os
import re
from unittest.case import TestCase

import jmespath

from checkov.terraform.checks.utils.dependency_path_handler import PATH_SEPARATOR, unify_dependency_path
from checkov.terraform.graph_builder.graph_components.block_types import BlockType
from checkov.terraform.graph_builder.graph_to_tf_definitions import convert_graph_vertices_to_tf_definitions
from checkov.terraform.graph_manager import GraphManager

TEST_DIRNAME = os.path.dirname(os.path.realpath(__file__))


class TestRendererScenarios(TestCase):

    def test_maze_of_variables(self):
        self.go('maze_of_variables')

    def test_merge_function(self):
        self.go("merge_function")

    def test_empty_file(self):
        self.go("empty_file")

    def test_simple_bucket_single_file(self):
        self.go("simple_bucket_single_file")

    def test_variable_defaults(self):
        self.go("variable_defaults")

    def test_variable_defaults_separate_files(self):
        self.go("variable_defaults_separate_files")

    def test_local_block(self):
        self.go("local_block")

    def test_local_bool_string_conversion(self):
        self.go("local_bool_string_conversion")

    def test_compound_local(self):
        self.go("compound_local")

    def test_concat_function(self):
        self.go("concat_function")

    def test_merge_function_unresolved_var(self):
        self.go("merge_function_unresolved_var", replace_expected=True)

    def test_tobool_function(self):
        self.go("tobool_function", {"JUNK": ['tobool("invalid")']})

    def test_tolist_function(self):
        self.go("tolist_function")

    def test_tomap_function(self):
        self.go("tomap_function")

    def test_map_function(self):
        self.go("map_function", {"INVALID_ODD_ARGS": ['map("only one")']})

    def test_tonumber_function(self):
        self.go("tonumber_function", {"INVALID": ['tonumber("no")']})

    def test_toset_function(self):
        self.go("toset_function", {"VAR": [{'c', 'b', 'a'}]})

    def test_tostring_function(self):
        self.go("tostring_function", {"INVALID_ARRAY": ['tostring([])']})

    def test_module_simple(self):
        self.go("module_simple")

    def test_module_simple_up_dir_ref(self):
        self.go("module_simple_up_dir_ref")

    def test_module_matryoshka(self):
        self.go("module_matryoshka")

    def test_list_default_622(self):            # see https://github.com/bridgecrewio/checkov/issues/622
        self.go("list_default_622", {"log_types_enabled": {'default': [['api',
              'audit',
              'authenticator',
              'controllerManager',
              'scheduler']],
 'type': ['list(string)']}})

    def test_module_reference(self):
        self.go("module_reference")

    def test_module_output_reference(self):
        self.go("module_output_reference")

    def test_bad_ref_fallbacks(self):
        self.go("bad_ref_fallbacks", replace_expected=True)

    def test_doc_evaluations_verify(self):
        self.go("doc_evaluations_verify", replace_expected=True)

    def test_bad_tf(self):
        # Note: this hits the _clean_bad_definitions internal function
        self.go("bad_tf")

    def test_colon(self):
        # Note: this hits the _clean_bad_definitions internal function
        self.go("colon", replace_expected=True)

    def test_null_variables_651(self):
        self.skipTest("different implementation, we keep the original variable reference")
        self.go("null_variables_651")

    def test_ternaries(self):
        self.go("ternaries")

    def test_ternary_793(self):
        self.go("ternary_793")

    def test_tfvars(self):
        self.go("tfvars")

    def test_account_dirs_and_modules(self):
        self.go("account_dirs_and_modules")

    def test_bogus_function(self):
        self.skipTest("invalid values are not supported")
        self.go("bogus_function")

    def go(self, dir_name, different_expected=None, replace_expected=False):
        os.environ['RENDER_VARIABLES_ASYNC'] = 'False'
        os.environ['LOG_LEVEL'] = 'INFO'
        different_expected = {} if not different_expected else different_expected
        resources_dir = os.path.realpath(
            os.path.join(TEST_DIRNAME, '../../../terraform/parser/resources/parser_scenarios', dir_name))
        graph_manager = GraphManager(dir_name, [dir_name])
        local_graph, _ = graph_manager.build_graph_from_source_directory(resources_dir, render_variables=True)
        got_tf_definitions, _ = convert_graph_vertices_to_tf_definitions(local_graph.vertices, resources_dir)
        expected = load_expected(replace_expected, dir_name, resources_dir)

        for expected_file, expected_block_type_dict in expected.items():
            module_removed_path = expected_file
            got_file = got_tf_definitions.get(module_removed_path)
            self.assertIsNotNone(got_file)
            for expected_block_type, expected_block_type_list in expected_block_type_dict.items():
                got_block_type_list = got_file.get(expected_block_type)
                self.assertIsNotNone(got_block_type_list)
                for expected_block_dict in expected_block_type_list:
                    for expected_block_name, expected_block_val in expected_block_dict.items():
                        if expected_block_type != BlockType.RESOURCE:
                            found = self.match_blocks(expected_block_val, different_expected, got_block_type_list,
                                                      expected_block_name)
                        else:
                            found = self.match_resources(expected_block_val, different_expected, got_block_type_list,
                                                         expected_block_name)
                        self.assertTrue(found,
                                        f"expected to find block {expected_block_dict} from file {expected_file} in graph")

    def match_blocks(self, expected_block_val, different_expected, got_block_type_list, expected_block_name):
        for got_block_dict in got_block_type_list:
            for got_block_name, got_block_val in got_block_dict.items():
                if got_block_name == expected_block_name:
                    if got_block_name in different_expected:
                        expected_block_val = different_expected.get(got_block_name)
                    self.assertEqual(expected_block_val, got_block_val,
                                     f"failed to match block [{got_block_name}].\nExpected: {expected_block_val}\nActual: {got_block_val}\n")
                    print(f"success {got_block_name}: {got_block_val}")
                    return True

        return False

    def match_resources(self, expected_block_val, different_expected, got_block_type_list, expected_block_name):
        for got_block_dict in got_block_type_list:
            for got_block_name, got_block_val in got_block_dict.items():
                if got_block_name == expected_block_name:
                    expected_resource_name = list(expected_block_val.keys())[0]
                    got_resource_name = list(got_block_val.keys())[0]
                    if expected_resource_name != got_resource_name:
                        continue
                    if expected_resource_name in different_expected:
                        expected_block_val = {expected_resource_name: different_expected.get(expected_resource_name)}
                    self.assertEqual(expected_block_val, got_block_val,
                                     f"failed to match block [{got_block_name}].\nExpected: {expected_block_val}\nActual: {got_block_val}\n")
                    print(f"success {got_block_name}: {got_block_val}")
                    return True

        return False


def load_expected(replace_expected, dir_name, resources_dir):
    if replace_expected:
        expected_file_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources")
        old_expected = load_expected_data(f"{dir_name}_expected.json", expected_file_dir)
        expected = {}
        for file_path in old_expected:
            new_file_path = file_path.replace(expected_file_dir, resources_dir)
            expected[new_file_path] = old_expected[file_path]
    else:
        expected = load_expected_data("expected.json", resources_dir)
    return expected


def load_expected_data(source_file_name, dir_path):
    expected_path = os.path.join(dir_path, source_file_name)
    if not os.path.exists(expected_path):
        return None

    with open(expected_path, "r") as f:
        expected_data = json.load(f)

    # Convert to absolute path:   "buckets/bucket.tf[main.tf#0]"
    #                              ^^^^^^^^^^^^^^^^^ ^^^^^^^
    #                                    HERE       & HERE
    #
    resolved_pattern = re.compile(r"(.+)\[(.+)#(\d+)]")  # groups:  location (1), referrer (2), index (3)

    # Expected files should have the filenames relative to their base directory, but the parser will
    # use the absolute path. This loop with replace relative filenames with absolute.
    keys = list(expected_data.keys())
    for key in keys:
        # NOTE: Sometimes keys have module referrers, sometimes they don't

        match = resolved_pattern.match(key)
        if match:
            new_key = _make_module_ref_absolute(match, dir_path)
        else:
            if os.path.isabs(key):
                continue
            new_key = os.path.join(dir_path, key)
        expected_data[new_key] = expected_data[key]
        del expected_data[key]

    for resolved_list in jmespath.search("*.module[].*[].__resolved__", expected_data):
        for list_index in range(0, len(resolved_list)):
            match = resolved_pattern.match(resolved_list[list_index])
            assert match is not None, f"Unexpected module resolved data: {resolved_list[list_index]}"
            resolved_list[list_index] = _make_module_ref_absolute(match, dir_path)
            # print(f"{match[0]} -> {resolved_list[list_index]}")

    return expected_data


def _make_module_ref_absolute(match, dir_path) -> str:
    module_location = match[1]
    if not os.path.isabs(module_location):
        module_location = os.path.join(dir_path, module_location)

    module_referrer = match[2]
    if PATH_SEPARATOR in module_referrer:
        module_referrer_fixed = []
        if '#' in module_referrer:
            module_referrer = module_referrer[:-2]
        for ref in module_referrer.split(PATH_SEPARATOR):
            if not os.path.isabs(ref):
                module_referrer_fixed.append(os.path.join(dir_path, ref))
        module_referrer = unify_dependency_path(module_referrer_fixed)
    else:
        module_referrer = os.path.join(dir_path, module_referrer)
    return f"{module_location}[{module_referrer}#{match[3]}]"
