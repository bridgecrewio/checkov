import dataclasses
import json
import os
import re
import unittest

import jmespath

from checkov.terraform.parser import Parser


def json_encoder(val):
    if dataclasses.is_dataclass(val):
        return dataclasses.asdict(val)
    if isinstance(val, set):
        return list(sorted(["__this_is_a_set__"] + list(val)))
    return val


class TestParserScenarios(unittest.TestCase):

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

    def test_merge_function(self):
        self.go("merge_function")

    def test_merge_function_unresolved_var(self):
        self.go("merge_function_unresolved_var")

    def test_tobool_function(self):
        self.go("tobool_function")

    def test_tolist_function(self):
        self.go("tolist_function")

    def test_tomap_function(self):
        self.go("tomap_function")

    def test_map_function(self):
        self.go("map_function")

    def test_tonumber_function(self):
        self.go("tonumber_function")

    def test_toset_function(self):
        self.go("toset_function")

    def test_tostring_function(self):
        self.go("tostring_function")

    def test_module_simple(self):
        self.go("module_simple")

    def test_module_simple_up_dir_ref(self):
        self.go("module_simple_up_dir_ref")

    def test_module_matryoshka(self):
        self.go("module_matryoshka")

    def test_list_default_622(self):            # see https://github.com/bridgecrewio/checkov/issues/622
        self.go("list_default_622")

    # TODO ROB - Implementation in progress
    # def test_formatting(self):
    #     self.go("formatting")

    def test_maze_of_variables(self):
        self.go("maze_of_variables")

    def test_module_reference(self):
        self.go("module_reference")

    def test_module_output_reference(self):
        self.go("module_output_reference")

    def test_bad_ref_fallbacks(self):
        self.go("bad_ref_fallbacks")

    def test_doc_evaluations_verify(self):
        self.go("doc_evaluations_verify")

    def test_bad_tf(self):
        # Note: this hits the _clean_bad_definitions internal function
        self.go("bad_tf")

    def test_colon(self):
        # Note: this hits the _clean_bad_definitions internal function
        self.go("colon")

    def test_null_variables_651(self):
        self.go("null_variables_651")

    @unittest.skip
    def test_count_index_scenario(self):
        # Run only manually, this test currently fails on multiple issues
        self.go("count_eval")

    @unittest.skip
    def test_json_807(self):
        self.go("json_807")

    def test_ternaries(self):
        self.go("ternaries")

    def test_ternary_793(self):
        self.go("ternary_793")

    def test_tfvars(self):
        self.go("tfvars")

    def test_account_dirs_and_modules(self):
        self.go("account_dirs_and_modules")

    def test_bogus_function(self):
        self.go("bogus_function")

    @staticmethod
    def go(dir_name):
        dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                f"resources/parser_scenarios/{dir_name}")
        assert os.path.exists(dir_path)

        expected_data = TestParserScenarios.load_expected_data("expected.json", dir_path)
        assert expected_data is not None, f"{dir_name}: expected.json file not found"

        evaluation_data = TestParserScenarios.load_expected_data("eval.json", dir_path)

        actual_data = {}
        actual_eval_data = {}
        errors = {}
        parser = Parser()
        parser.parse_directory(dir_path, actual_data, actual_eval_data, errors, download_external_modules=True)
        assert not errors, f"{dir_name}: Unexpected errors: {errors}"
        definition_string = json.dumps(actual_data, indent=2, default=json_encoder)
        definition_encoded = json.loads(definition_string)
        assert definition_encoded == expected_data, \
            f"{dir_name}: Data mismatch:\n" \
            f"  Expected: \n{json.dumps(expected_data, indent=2, default=json_encoder)}\n\n" \
            f"  Actual: \n{definition_string}"

        if evaluation_data is not None:
            definition_string = json.dumps(actual_eval_data, indent=2, default=json_encoder)
            definition_encoded = json.loads(definition_string)
            assert definition_encoded == evaluation_data, \
                f"{dir_name}: Evaluation data mismatch:\n" \
                f"  Expected: \n{json.dumps(evaluation_data, indent=2, default=json_encoder)}\n\n" \
                f"  Actual: \n{definition_string}"

    @staticmethod
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
        resolved_pattern = re.compile(r"(.+)\[(.+)#(\d+)]")   # groups:  location (1), referrer (2), index (3)

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
    if not os.path.isabs(module_referrer):
        module_referrer = os.path.join(dir_path, module_referrer)
    return f"{module_location}[{module_referrer}#{match[3]}]"


if __name__ == '__main__':
    unittest.main()
