import os

from lark import Tree

from checkov.terraform import TFDefinitionKey
from checkov.terraform.modules.module_utils import clean_parser_types
from checkov.terraform.tf_parser import TFParser
from unittest import TestCase

TEST_DIRNAME = os.path.dirname(os.path.realpath(__file__))


class TestParser(TestCase):
    def test_bool_parsing_avoid_remove_non_existing(self):
        conf = {'test': ['Bool'], 'variable': ['aws:SecureTransport'], 'values': [['false']]}
        actual = clean_parser_types(conf)
        expected = {'test': ['Bool'], 'variable': ['aws:SecureTransport'], 'values': [[False]]}
        self.assertDictEqual(expected, actual)

    def test_bool_parsing_sort_only_lists(self):
        conf = {'enabled_metrics': [['a', 'c', 'b'], 'b', 'a', 'c']}
        actual = clean_parser_types(conf)
        expected = {'enabled_metrics': [['a', 'b', 'c'], 'a', 'b', 'c']}
        self.assertDictEqual(expected, actual)

    def test_bool_parsing_sort_only_lists_with_bools(self):
        conf = {'enabled_metrics': [['a', 'true', 'false'], 'b', 'true', 'false']}
        actual = clean_parser_types(conf)
        expected = {'enabled_metrics': [[True, False, 'a'], True, False, 'b']}
        self.assertDictEqual(expected, actual)

    def test_set_parsing_to_list(self):
        conf = {'enabled_metrics': [['a', 'true', 'false'], 'b', 'true', 'false'], 'example_set': [{'1', '2', '3'}]}
        actual = clean_parser_types(conf)
        expected = {'enabled_metrics': [[True, False, 'a'], True, False, 'b'], 'example_set': [['1', '2', '3']]}
        self.assertDictEqual(expected, actual)

    def test_tree_parsing_to_str(self):
        conf = {'enabled_metrics': [['a', 'true', 'false'], 'b', 'true', 'false'], 'example_set': Tree("data", ["child1", "child2"])}
        actual = clean_parser_types(conf)
        expected = {'enabled_metrics': [[True, False, 'a'], True, False, 'b'], 'example_set': 'Tree(\'data\', [\'child1\', \'child2\'])'}
        self.assertDictEqual(expected, actual)

    def test_hcl_parsing_consistent_old_new(self):
        cur_dir = os.path.dirname(os.path.realpath(__file__))
        tf_dir = f'{cur_dir}/../resources/tf_parsing_comparison/tf_regular'
        old_tf_dir = f'{cur_dir}/../resources/tf_parsing_comparison/tf_old'
        _, tf_definitions = TFParser().parse_hcl_module(tf_dir, 'AWS')
        _, old_tf_definitions = TFParser().parse_hcl_module(old_tf_dir, 'AWS')
        definition_value = list(tf_definitions.values())[0]
        old_definition_value = list(tf_definitions.values())[0]
        self.assertDictEqual(definition_value, old_definition_value)

    def test_hcl_parsing_old_booleans_correctness(self):
        cur_dir = os.path.dirname(os.path.realpath(__file__))
        tf_dir = f'{cur_dir}/../resources/tf_parsing_comparison/tf_regular'
        _, tf_definitions = TFParser().parse_hcl_module(tf_dir, 'AWS')
        expected = [
            {
                "aws_cloudtrail": {
                    "tfer--cashdash_trail": {
                        "__end_line__": 11,
                        "__start_line__": 1,
                        "enable_log_file_validation": [True],
                        "enable_logging": [True],
                        "include_global_service_events": [True],
                        "is_multi_region_trail": [True],
                        "is_organization_trail": [False],
                        "kms_key_id": ["arn:aws:kms:us-east-1:098885917934:key/5e7c4a79-bd63-42ca-9ae0-8f8e41f9c2f1"],
                        "name": ["cashdash_trail"],
                        "s3_bucket_name": ["cashdash-trail"],
                        "sns_topic_name": ["arn:aws:sns:us-east-1:098885917934:clodtrail-sns-topic"],
                    }
                }
            },
            {
                "google_compute_instance": {
                    "tfer--sentry-002D-v1": {
                        "__end_line__": 67,
                        "__start_line__": 13,
                        "attached_disk": [
                            {
                                "device_name": ["sentry"],
                                "mode": ["READ_WRITE"],
                                "source": [
                                    "https://www.googleapis.com/compute/v1/projects/be-base-wksp-v1/zones/us-west3-b/disks/sentry-data-v1"
                                ],
                            }
                        ],
                        "boot_disk": [
                            {
                                "auto_delete": [True],
                                "device_name": ["persistent-disk-0"],
                                "initialize_params": [
                                    {
                                        "image": [
                                            "https://www.googleapis.com/compute/v1/projects/debian-cloud/global/images/debian-10-buster-v20200910"
                                        ],
                                        "size": ["10"],
                                        "type": ["pd-standard"],
                                    }
                                ],
                                "kms_key_self_link": [
                                    "projects/acme-project/locations/global/keyRings/global-v1/cryptoKeys/global-disk-key"
                                ],
                                "mode": ["READ_WRITE"],
                                "source": [
                                    "https://www.googleapis.com/compute/v1/projects/acme-project/zones/us-west3-b/disks/sentry-v1"
                                ],
                            }
                        ],
                        "can_ip_forward": [False],
                        "deletion_protection": [False],
                        "enable_display": [False],
                        "machine_type": ["n1-standard-2"],
                        "metadata": [{"block-project-ssh-keys": True, "some-other-attribute": False}],
                        "name": ["sentry-v1"],
                        "network_interface": [
                            {
                                "access_config": [{"nat_ip": ["34.106.48.192"], "network_tier": ["PREMIUM"]}],
                                "network": [
                                    "https://www.googleapis.com/compute/v1/projects/acme-project/global/networks/acme"
                                ],
                                "network_ip": ["10.40.0.53"],
                                "subnetwork": [
                                    "https://www.googleapis.com/compute/v1/projects/acme-project/regions/us-west3/subnetworks/sentry"
                                ],
                                "subnetwork_project": ["acme-project"],
                            }
                        ],
                        "project": ["acme-project"],
                        "scheduling": [
                            {"automatic_restart": [True], "on_host_maintenance": ["MIGRATE"], "preemptible": [False]}
                        ],
                        "service_account": [
                            {
                                "email": ["sentry-vm@acme-project.iam.gserviceaccount.com"],
                                "scopes": [
                                    [
                                        "https://www.googleapis.com/auth/devstorage.read_only",
                                        "https://www.googleapis.com/auth/logging.write",
                                        "https://www.googleapis.com/auth/monitoring.write",
                                        "https://www.googleapis.com/auth/userinfo.email",
                                    ]
                                ],
                            }
                        ],
                        "shielded_instance_config": [
                            {
                                "enable_integrity_monitoring": [True],
                                "enable_secure_boot": [False],
                                "enable_vtpm": [True],
                            }
                        ],
                        "tags": [["allow-sentry", "allow-ssh"]],
                        "zone": ["us-west3-b"],
                    }
                }
            },
        ]
        definition_key = TFDefinitionKey(file_path="/Users/bfatal/Documents/code/checkov/tests/terraform/graph/graph_builder/../resources/tf_parsing_comparison/tf_regular/main.tf",
                                         tf_source_modules=None)
        tf_definitions_resources = tf_definitions[definition_key]['resource']
        for index in range(len(tf_definitions_resources)):
            self.assertDictEqual(
                tf_definitions_resources[index],
                expected[index]
            )

    def test_hcl_parsing_sorting(self):
        source_dir = os.path.realpath(os.path.join(TEST_DIRNAME,
                                                   '../resources/tf_parsing_comparison/modifications_diff'))
        config_parser = TFParser()
        _, tf_definitions = config_parser.parse_hcl_module(source_dir, 'AWS')
        expected = ['https://www.googleapis.com/auth/devstorage.read_only', 'https://www.googleapis.com/auth/logging.write',
                    'https://www.googleapis.com/auth/monitoring.write', 'https://www.googleapis.com/auth/service.management.readonly',
                    'https://www.googleapis.com/auth/servicecontrol', 'https://www.googleapis.com/auth/trace.append']
        defintion_key = TFDefinitionKey(file_path="/Users/bfatal/Documents/code/checkov/tests/terraform/graph/resources/tf_parsing_comparison/modifications_diff/main.tf",
                              tf_source_modules=None)
        result_resource = tf_definitions[defintion_key]['resource'][0]['google_compute_instance']['tfer--test3']['service_account'][0]['scopes'][0]
        self.assertListEqual(result_resource, expected)

    def test_build_graph_with_linked_modules(self):
        source_dir = os.path.realpath(os.path.join(TEST_DIRNAME,
                                                   '../resources/nested_modules_double_call'))
        config_parser = TFParser()

        definitions = config_parser.parse_directory(source_dir)
        assert len(definitions.keys()) == 13
        assert '/Users/arosenfeld/Desktop/dev/checkov/tests/terraform/graph/resources/nested_modules_double_call/main.tf' not in definitions
        assert '/Users/arosenfeld/Desktop/dev/checkov/tests/terraform/graph/resources/nested_modules_double_call/third/main.tf[/Users/arosenfeld/Desktop/dev/checkov/tests/terraform/graph/resources/nested_modules_double_call/main.tf#0]' not in definitions
        assert '/Users/arosenfeld/Desktop/dev/checkov/tests/terraform/graph/resources/nested_modules_double_call/four/main.tf[/Users/arosenfeld/Desktop/dev/checkov/tests/terraform/graph/resources/nested_modules_double_call/third/main.tf#0[/Users/arosenfeld/Desktop/dev/checkov/tests/terraform/graph/resources/nested_modules_double_call/main.tf#0]]' not in definitions
        assert '/Users/arosenfeld/Desktop/dev/checkov/tests/terraform/graph/resources/nested_modules_double_call/third/main.tf' not in definitions
        assert '/Users/arosenfeld/Desktop/dev/checkov/tests/terraform/graph/resources/nested_modules_double_call/four/main.tf[/Users/arosenfeld/Desktop/dev/checkov/tests/terraform/graph/resources/nested_modules_double_call/third/main.tf#0]' not in definitions
