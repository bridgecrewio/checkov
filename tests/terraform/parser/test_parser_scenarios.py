import dataclasses
import json
import os
import unittest

import dpath
import itertools

from checkov.terraform import parser2


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

    def test_local_block(self):
        self.go("local_block")

    def test_local_bool_string_conversion(self):
        self.go("local_bool_string_conversion")

    def test_compound_local(self):
        self.go("compound_local")

    def test_tobool_function(self):
        self.go("tobool_function")

    def test_tolist_function(self):
        self.go("tolist_function")

    def test_tomap_function(self):
        self.go("tomap_function")

    def test_tonumber_function(self):
        self.go("tonumber_function")

    def test_toset_function(self):
        self.go("toset_function")

    def test_tostring_function(self):
        self.go("tostring_function")

    def test_module_simple(self):
        self.go("module_simple")

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

    def go(self, dir_name):
        dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                f"resources/parser_scenarios/{dir_name}")
        assert os.path.exists(dir_path)

        expected_data = TestParserScenarios.load_expected_data("expected.json", dir_path, dir_name)
        assert expected_data is not None, f"{dir_name}: expected.json file not found"

        evaluation_data = TestParserScenarios.load_expected_data("eval.json", dir_path, dir_name)

        actual_data = {}
        actual_eval_data = {}
        errors = {}
        parser2._parse_directory(dir_path, False, actual_data, actual_eval_data, errors)
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
    def load_expected_data(source_file_name, dir_path, dir_name):
        expected_path = os.path.join(dir_path, source_file_name)
        if not os.path.exists(expected_path):
            return None

        with open(expected_path, "r") as f:
            expected_data = json.load(f)

        # Expected files should have the filenames relative to their base directory, but the parser will
        # use the absolute path. This loop with replace relative filenames with absolute.
        top_level_tuple = None, expected_data
        for _, data in itertools.chain([top_level_tuple],
                                       dpath.search(expected_data, "**/__resolved__", yielded=True)):

            keys = list(data.keys())
            for key in keys:
                if os.path.isabs(key):
                    continue
                data[os.path.join(dir_path, key)] = data[key]
                del data[key]

        return expected_data


if __name__ == '__main__':
    unittest.main()
