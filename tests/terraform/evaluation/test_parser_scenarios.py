import json
import os
import unittest

from checkov.terraform import parser2


class TestParserScenarios(unittest.TestCase):

    def test_scenarios(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        for entry in os.scandir(os.path.join(current_dir, "resources/parser_scenarios")):
            if not entry.is_dir():
                continue

            with self.subTest(entry.name):
                expected_data = TestParserScenarios.load_expected_data(entry)

                tf_definitions = {}
                errors = {}
                parser2.parse_directory(entry.path, tf_definitions, {}, {}, errors)
                assert not errors, f"{entry.name}: Unexpected errors: {errors}"
                assert tf_definitions == expected_data, f"{entry.name}: Data mismatch:\n" \
                                                        f"  Expected: \n{expected_data}\n\n" \
                                                        f"  Actual: \n{tf_definitions}"

    @staticmethod
    def load_expected_data(dir_entry):
        expected_path = os.path.join(dir_entry.path, "expected.json")
        assert os.path.exists(expected_path), f"{dir_entry.name}: expected.json file not found"

        with open(expected_path, "r") as f:
            expected_data = json.load(f)

        # Expected files should have the filenames relative to their base directory, but the parser will
        # use the absolute path. This loop with replace relative filenames with absolute.
        keys = list(expected_data.keys())
        for key in keys:
            if os.path.isabs(key):
                continue
            expected_data[os.path.join(dir_entry.path, key)] = expected_data[key]
            del expected_data[key]

        return expected_data


if __name__ == '__main__':
    unittest.main()
