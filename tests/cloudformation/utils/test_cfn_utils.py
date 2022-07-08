import os
import unittest
from pathlib import Path

from checkov.cloudformation.cfn_utils import get_folder_definitions, build_definitions_context
from checkov.common.bridgecrew.integration_features.features.policy_metadata_integration import integration as metadata_integration
from checkov.common.bridgecrew.platform_integration import bc_integration, BcPlatformIntegration
from checkov.common.parsers.node import DictNode
from checkov.cloudformation.parser import TemplateSections

TEST_DIRNAME = os.path.dirname(os.path.realpath(__file__))
RELATIVE_PATH = "file_formats"


class TestCfnUtils(unittest.TestCase):
    def setUp(self):
        # self.test_root_dir = os.path.realpath(os.path.join(TEST_DIRNAME, RELATIVE_PATH))
        self.test_root_dir = Path(TEST_DIRNAME) / RELATIVE_PATH
        integration = BcPlatformIntegration()
        metadata_integration.bc_integration = integration
        integration.get_public_run_config()
        metadata_integration.pre_scan()
        definitions, definitions_raw = get_folder_definitions(str(self.test_root_dir), None)
        self.definitions_context = build_definitions_context(definitions, definitions_raw)

    def tearDown(self) -> None:
        metadata_integration.bc_integration = bc_integration

    def validate_definition_lines(self, definition: DictNode, start_line, end_line, code_lines):
        self.assertEqual(definition["start_line"], start_line)
        self.assertEqual(definition["end_line"], end_line)
        self.assertEqual(len(definition["code_lines"]), code_lines)

    def test_parameters_value(self):
        # Asserting test.yaml file
        yaml_parameters = self.definitions_context[str(self.test_root_dir / "test.yaml")][
            TemplateSections.PARAMETERS.value
        ]
        self.assertIsNotNone(yaml_parameters)
        self.assertEqual(len(yaml_parameters), 2)
        self.validate_definition_lines(yaml_parameters["KmsMasterKeyId"], 4, 7, 4)
        self.validate_definition_lines(yaml_parameters["DBName"], 8, 11, 4)
        # Asserting test2.yaml file
        yaml2_parameters = self.definitions_context[str(self.test_root_dir / "test2.yaml")][
            TemplateSections.PARAMETERS.value
        ]
        self.assertIsNotNone(yaml2_parameters)
        self.assertEqual(len(yaml2_parameters), 1)
        self.validate_definition_lines(yaml2_parameters["LatestAmiId"], 4, 6, 3)
        # Asserting json file
        json_parameters = self.definitions_context[str(self.test_root_dir / "test.json")][
            TemplateSections.PARAMETERS.value
        ]
        self.assertIsNotNone(json_parameters)
        self.assertEqual(len(json_parameters), 2)
        self.validate_definition_lines(json_parameters["KmsMasterKeyId"], 5, 9, 5)
        self.validate_definition_lines(json_parameters["DBName"], 10, 14, 5)

    def test_resources_value(self):
        # Asserting test.yaml file
        yaml_resources = self.definitions_context[str(self.test_root_dir / "test.yaml")][
            TemplateSections.RESOURCES.value
        ]
        self.assertIsNotNone(yaml_resources)
        self.assertEqual(len(yaml_resources), 2)
        self.validate_definition_lines(yaml_resources["MySourceQueue"], 13, 16, 4)
        self.validate_definition_lines(yaml_resources["MyDB"], 17, 37, 21)
        # Asserting test2.yaml file
        yaml2_resources = self.definitions_context[str(self.test_root_dir / "test2.yaml")][
            TemplateSections.RESOURCES.value
        ]
        self.assertIsNotNone(yaml2_resources)
        self.assertEqual(len(yaml2_resources), 4)
        self.validate_definition_lines(yaml2_resources["WebHostStorage"], 12, 23, 12)
        self.validate_definition_lines(yaml2_resources["LogsKey"], 29, 44, 16)
        self.validate_definition_lines(yaml2_resources["LogsKeyAlias"], 46, 50, 5)
        self.validate_definition_lines(yaml2_resources["DBAppInstance"], 52, 184, 133)
        # Asserting json file
        json_resources = self.definitions_context[str(self.test_root_dir / "test.json")][
            TemplateSections.RESOURCES.value
        ]
        self.assertIsNotNone(json_resources)
        self.assertEqual(len(json_resources), 2)
        self.validate_definition_lines(json_resources["MySourceQueue"], 17, 22, 6)
        self.validate_definition_lines(json_resources["MyDB"], 23, 32, 10)

    def test_outputs_value(self):
        # Asserting test.yaml file
        yaml_outputs = self.definitions_context[str(self.test_root_dir / "test.yaml")][TemplateSections.OUTPUTS.value]
        self.assertIsNotNone(yaml_outputs)
        self.assertEqual(len(yaml_outputs), 1)
        self.validate_definition_lines(yaml_outputs["DBAppPublicDNS"], 40, 42, 3)
        # Asserting test2.yaml file
        yaml2_outputs = self.definitions_context[str(self.test_root_dir / "test2.yaml")][TemplateSections.OUTPUTS.value]
        self.assertIsNotNone(yaml2_outputs)
        self.assertEqual(len(yaml2_outputs), 5)
        self.validate_definition_lines(yaml2_outputs["EC2PublicDNS"], 187, 191, 5)
        self.validate_definition_lines(yaml2_outputs["VpcId"], 192, 195, 4)
        self.validate_definition_lines(yaml2_outputs["PublicSubnet"], 196, 198, 3)
        self.validate_definition_lines(yaml2_outputs["PublicSubnet2"], 200, 202, 3)
        self.validate_definition_lines(yaml2_outputs["UserName"], 204, 206, 3)
        # Asserting json file
        json_outputs = self.definitions_context[str(self.test_root_dir / "test.json")][TemplateSections.OUTPUTS.value]
        self.assertIsNotNone(json_outputs)
        self.assertEqual(len(json_outputs), 1)
        self.validate_definition_lines(json_outputs["DBAppPublicDNS"], 35, 38, 4)

    def test_skipped_check_exists(self):
        skipped_checks = self.definitions_context[str(self.test_root_dir / "test.yaml")][
            TemplateSections.RESOURCES.value
        ]["MyDB"]["skipped_checks"]
        self.assertEqual(len(skipped_checks), 3)
        self.assertCountEqual(
            skipped_checks,
            [
                {
                    "id": "CKV_AWS_16",
                    "suppress_comment": "Ensure all data stored in the RDS is securely encrypted at rest",
                    "bc_id": "BC_AWS_GENERAL_4",
                    "line_number": 30
                },
                {
                    "id": "CKV_AWS_17",
                    "suppress_comment": "Ensure all data stored in RDS is not publicly accessible",
                    "bc_id": "BC_AWS_PUBLIC_2",
                },
                {
                    "id": "CKV_AWS_157",
                    "suppress_comment": "Ensure that RDS instances have Multi-AZ enabled",
                    "bc_id": "BC_AWS_GENERAL_73",
                },
            ],
        )


if __name__ == "__main__":
    unittest.main()
