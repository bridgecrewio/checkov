import os
import unittest
from pathlib import Path

from checkov.common.parsers.node import DictNode
from checkov.bicep.parser import Parser
from checkov.bicep.utils import get_scannable_file_paths
from checkov.bicep.graph_builder.context_definitions import build_definitions_context, DEFINITIONS_KEYS_TO_PARSE

TEST_DIRNAME = os.path.dirname(os.path.realpath(__file__))
RELATIVE_PATH = "resources"
FILE1_NAME = "definitions_example1.bicep"
FILE2_NAME = "definitions_example2.bicep"


class TestDefinitionsContext(unittest.TestCase):
    def setUp(self):
        self.test_root_dir = Path(TEST_DIRNAME) / RELATIVE_PATH
        bicep_parser = Parser()
        self.files_path = get_scannable_file_paths(self.test_root_dir)
        definitions, definitions_raw, parsing_errors = bicep_parser.get_files_definitions(file_paths=self.files_path)
        self.definitions_context = build_definitions_context(definitions, definitions_raw)
        self.file1 = self.definitions_context[f"{self.test_root_dir}/{FILE1_NAME}"]
        self.file2 = self.definitions_context[f"{self.test_root_dir}/{FILE2_NAME}"]

    def test_parameters_values(self):
        self.assertEqual(len(self.definitions_context), len(self.files_path))

        file1_parameters = self.file1[DEFINITIONS_KEYS_TO_PARSE["parameters"]]
        self.assertEqual(len(file1_parameters), 5)
        self.validate_definition_lines(file1_parameters["adminUsername"], 4, 5, 2)
        assert file1_parameters["adminUsername"]["type"] == "string"
        self.validate_definition_lines(file1_parameters["storageAccountType"], 11, 16, 6)
        assert file1_parameters["storageAccountType"]["type"] == "string"
        self.validate_definition_lines(file1_parameters["virtualMachineSize"], 1, 2, 2)
        assert file1_parameters["virtualMachineSize"]["type"] == "string"

        file2_parameters = self.file2[DEFINITIONS_KEYS_TO_PARSE["parameters"]]
        self.assertEqual(len(file2_parameters), 9)
        self.validate_definition_lines(file2_parameters["virtualMachineName"], 1, 1, 1)
        assert file2_parameters["virtualMachineName"]["type"] == "string"
        self.validate_definition_lines(file2_parameters["acrName"], 5, 5, 1)
        assert file2_parameters["acrName"]["type"] == "string"
        self.validate_definition_lines(file2_parameters["publicKey4"], 24, 29, 6)
        assert file2_parameters["publicKey4"]["type"] == "object"

    def test_resources_value(self):
        file1_resources = self.file1[DEFINITIONS_KEYS_TO_PARSE["resources"]]
        self.assertEqual(len(file1_resources), 8)
        self.validate_definition_lines(file1_resources["Microsoft.Compute/virtualMachines.vm"], 33, 82, 50)
        self.validate_definition_lines(file1_resources["Microsoft.Storage/storageAccounts.diagsAccount"], 84, 93, 10)
        self.validate_definition_lines(file1_resources["Microsoft.Network/virtualNetworks.vnet"], 102, 129, 28)

        file2_resources = self.file2[DEFINITIONS_KEYS_TO_PARSE["resources"]]
        self.assertEqual(len(file2_resources), 1)
        self.validate_definition_lines(file2_resources["Microsoft.Compute/virtualMachines.vm"], 31, 72, 42)

    def test_skipped_check_exists(self):
        skipped_checks = self.file1[DEFINITIONS_KEYS_TO_PARSE["resources"]]["Microsoft.Storage/storageAccounts.diagsAccount"]["skipped_checks"]
        self.assertCountEqual(
            skipped_checks,
            {"CKV_AZURE_35":
                 {"result": "SKIPPED", "suppress_comment": " just skip it"},
             "CKV_AZURE_36":
                 {"result": "SKIPPED", "suppress_comment": " skip that too"}
             }
        )

    def validate_definition_lines(self, definition: DictNode, start_line, end_line, code_lines):
        self.assertEqual(definition["start_line"], start_line)
        self.assertEqual(definition["end_line"], end_line)
        self.assertEqual(len(definition["code_lines"]), code_lines)
