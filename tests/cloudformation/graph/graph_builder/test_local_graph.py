import os
from pathlib import Path
from unittest import TestCase
from checkov.common.graph.graph_builder.graph_components.attribute_names import CustomAttributes
from checkov.cloudformation.cfn_utils import create_definitions
from checkov.cloudformation.graph_builder.graph_components.block_types import BlockType
from checkov.cloudformation.graph_builder.graph_to_definitions import convert_graph_vertices_to_definitions
from checkov.cloudformation.graph_builder.graph_components.generic_resource_encryption import ENCRYPTION_BY_RESOURCE_TYPE
from checkov.cloudformation.graph_builder.local_graph import CloudformationLocalGraph
from checkov.common.graph.graph_builder import EncryptionValues, EncryptionTypes
from checkov.cloudformation.parser import parse, TemplateSections
from checkov.runner_filter import RunnerFilter

TEST_DIRNAME = os.path.dirname(os.path.realpath(__file__))


class TestLocalGraph(TestCase):
    def test_build_graph_with_single_resource(self):
        relative_file_path = "../../checks/resource/aws/example_APIGatewayXray/APIGatewayXray-PASSED.yaml"
        definitions = {}
        file = os.path.realpath(os.path.join(TEST_DIRNAME, relative_file_path))
        (definitions[relative_file_path], definitions_raw) = parse(file)
        local_graph = CloudformationLocalGraph(definitions)
        local_graph.build_graph(render_variables=False)
        self.assertEqual(1, len(local_graph.vertices))
        self.assertEqual(0, len(local_graph.edges))
        resource_vertex = local_graph.vertices[0]
        self.assertEqual("AWS::ApiGateway::Stage.Enabled", resource_vertex.name)
        self.assertEqual("AWS::ApiGateway::Stage.Enabled", resource_vertex.id)
        self.assertEqual(BlockType.RESOURCE, resource_vertex.block_type)
        self.assertEqual("CloudFormation", resource_vertex.source)
        self.assertDictEqual(definitions[relative_file_path]["Resources"]["Enabled"]["Properties"],
                             resource_vertex.attributes)

    def test_build_graph_with_params_outputs(self):
        relative_file_path = "../../checks/resource/aws/example_IAMRoleAllowAssumeFromAccount/example_IAMRoleAllowAssumeFromAccount-PASSED-2.yml"
        definitions = {}
        file = os.path.realpath(os.path.join(TEST_DIRNAME, relative_file_path))
        (definitions[relative_file_path], definitions_raw) = parse(file)
        local_graph = CloudformationLocalGraph(definitions)
        local_graph.build_graph(render_variables=False)
        self.assertEqual(len(local_graph.vertices), 57)
        self.assertEqual(len([v for v in local_graph.vertices if v.block_type == BlockType.CONDITIONS]), 2)
        self.assertEqual(len([v for v in local_graph.vertices if v.block_type == BlockType.RESOURCE]), 16)
        self.assertEqual(len([v for v in local_graph.vertices if v.block_type == BlockType.PARAMETERS]), 30)
        self.assertEqual(len([v for v in local_graph.vertices if v.block_type == BlockType.OUTPUTS]), 8)
        self.assertEqual(len([v for v in local_graph.vertices if v.block_type == BlockType.MAPPINGS]), 1)

    def test_vertices_from_local_graph(self):
        resources_dir = os.path.realpath(os.path.join(TEST_DIRNAME, './resources/vertices'))
        definitions, _ = create_definitions(root_folder=resources_dir, files=None, runner_filter=RunnerFilter())
        local_graph = CloudformationLocalGraph(definitions)
        local_graph.build_graph(render_variables=False)
        definitions, breadcrumbs = convert_graph_vertices_to_definitions(local_graph.vertices, resources_dir)

        self.assertIsNotNone(definitions)
        self.assertEqual(len(definitions.items()), 2)

        test_yaml_definitions = definitions[os.path.join(resources_dir, 'test.yaml')][TemplateSections.RESOURCES]
        self.assertEqual(len(test_yaml_definitions.keys()), 2)
        self.assertIn('MyDB', test_yaml_definitions.keys())
        self.assertIn('MySourceQueue', test_yaml_definitions.keys())

        test_json_definitions = definitions[os.path.join(resources_dir, 'test.json')][TemplateSections.RESOURCES]
        self.assertEqual(len(test_json_definitions.keys()), 2)
        self.assertIn('MyDB', test_json_definitions.keys())
        self.assertIn('MySourceQueue', test_json_definitions.keys())

        self.assertIsNotNone(breadcrumbs)
        self.assertDictEqual(breadcrumbs, {})  # Will be changed when we add breadcrumbs to cfn vertices

    def test_yaml_conditioned_vertices_from_local_graph(self):
        root_dir = os.path.realpath(os.path.join(TEST_DIRNAME, './resources/conditioned_vertices/yaml'))
        file_name = 'test.yaml'
        self.validate_conditioned_vertices_from_local_graph(root_dir, file_name)

    def test_json_conditioned_vertices_from_local_graph(self):
        root_dir = os.path.realpath(os.path.join(TEST_DIRNAME, './resources/conditioned_vertices/json'))
        file_name = 'test.json'
        self.validate_conditioned_vertices_from_local_graph(root_dir, file_name)

    def validate_conditioned_vertices_from_local_graph(self, root_dir, file_name):
        true_condition_resources = {'BucketFnEqualsTrue', 'BucketFnNotTrue', 'BucketFnNotTrueThroughCondition',
                             'BucketFnAndTrue', 'BucketFnAndTrueWithCondition',
                             'BucketFnOrTrue', 'BucketFnOrTrueWithCondition'}
        definitions, _ = create_definitions(root_folder=root_dir, files=None, runner_filter=RunnerFilter())
        local_graph = CloudformationLocalGraph(definitions)
        local_graph.build_graph(render_variables=True)
        definitions, breadcrumbs = convert_graph_vertices_to_definitions(local_graph.vertices, root_dir)

        self.assertIsNotNone(definitions)
        self.assertEqual(len(definitions.items()), 1)

        test_yaml_definitions = definitions[os.path.join(root_dir, file_name)][TemplateSections.RESOURCES]
        definitions_set = set(test_yaml_definitions.keys())
        self.assertEqual(len(definitions_set), 7)
        self.assertSetEqual(true_condition_resources, definitions_set)

    def test_yaml_edges(self):
        root_dir = os.path.realpath(os.path.join(TEST_DIRNAME, 'resources/edges_yaml'))
        self.validate_edges_count(root_dir)

    def test_json_edges(self):
        root_dir = os.path.realpath(os.path.join(TEST_DIRNAME, 'resources/edges_json'))
        self.validate_edges_count(root_dir)

    def validate_edges_count(self, root_dir) -> None:
        expected_out_edges_count = {
            'parameters.EnvType': 0,
            'parameters.DataBucketName': 0,
            'mappings.RegionMap': 0,
            'conditions.CreateProdResources': 1,
            'conditions.CreateDevResources': 1,
            'AWS::EC2::Instance.EC2Instance': 4,
            'AWS::EC2::VolumeAttachment.MountPoint': 3,
            'AWS::EC2::Volume.NewVolume': 2,
            'AWS::S3::Bucket.DataBucket': 4,
            'outputs.EC2InstanceId': 1,
            'outputs.EC2PublicDNS': 1,
            'outputs.DataBucketUniqueId': 2
        }

        expected_in_edges_count = {
            'parameters.EnvType': 4,
            'parameters.DataBucketName': 3,
            'mappings.RegionMap': 1,
            'conditions.CreateProdResources': 3,
            'conditions.CreateDevResources': 1,
            'AWS::EC2::Instance.EC2Instance': 5,
            'AWS::EC2::VolumeAttachment.MountPoint': 0,
            'AWS::EC2::Volume.NewVolume': 1,
            'AWS::S3::Bucket.DataBucket': 1,
            'outputs.EC2InstanceId': 0,
            'outputs.EC2PublicDNS': 0,
            'outputs.DataBucketUniqueId': 0
        }

        definitions, _ = create_definitions(root_folder=root_dir, files=None, runner_filter=RunnerFilter())
        local_graph = CloudformationLocalGraph(definitions)
        local_graph.build_graph(render_variables=False)
        idx_to_vertex_id = {idx: vertex.id for idx, vertex in enumerate(local_graph.vertices)}

        # we check that each entity in the template file has the right amount of out edges_yaml
        out_edges_overall_count = 0
        for vertex_index, actual_out_edges in local_graph.out_edges.items():
            vertex_id = idx_to_vertex_id[vertex_index]
            self.assertEqual(len(actual_out_edges), expected_out_edges_count[vertex_id], f'{vertex_id} actually has {len(actual_out_edges)} outgoing edges, not {expected_out_edges_count[vertex_id]}')
            out_edges_overall_count += len(actual_out_edges)

        # we check that each entity in the template file has the right amount of in edges_yaml
        in_edges_overall_count = 0
        for vertex_index, actual_in_edges in local_graph.in_edges.items():
            vertex_id = idx_to_vertex_id[vertex_index]
            self.assertEqual(len(actual_in_edges), expected_in_edges_count[vertex_id], f'{vertex_id} actually has {len(actual_in_edges)} outgoing edges, not {expected_in_edges_count[vertex_id]}')
            in_edges_overall_count += len(actual_in_edges)

        # we check that the overall amount of out edges_yaml equals the overall amount of in edges_yaml
        # and the overall amount of edges_yaml
        self.assertEqual(out_edges_overall_count, in_edges_overall_count)
        self.assertEqual(out_edges_overall_count, len(local_graph.edges))

    def test_build_graph_with_sam_resource(self):
        sam_file_path = Path(TEST_DIRNAME) / "resources/sam/template.yaml"

        definitions, _ = create_definitions(root_folder="", files=[str(sam_file_path)], runner_filter=RunnerFilter())
        local_graph = CloudformationLocalGraph(definitions)
        local_graph.build_graph(render_variables=False)

        self.assertEqual(len(local_graph.vertices), 8)
        self.assertEqual(len([v for v in local_graph.vertices if v.block_type == BlockType.GLOBALS]), 1)
        self.assertEqual(len([v for v in local_graph.vertices if v.block_type == BlockType.RESOURCE]), 3)
        self.assertEqual(len([v for v in local_graph.vertices if v.block_type == BlockType.OUTPUTS]), 1)
        self.assertEqual(len([v for v in local_graph.vertices if v.block_type == BlockType.MAPPINGS]), 1)

        function_1_index = local_graph.vertices_block_name_map["resource"]["AWS::Serverless::Function.Function1"][0]
        function_2_index = local_graph.vertices_block_name_map["resource"]["AWS::Serverless::Function.Function2"][0]
        function_1_vertex = local_graph.vertices[function_1_index]
        function_2_vertex = local_graph.vertices[function_2_index]

        # SAM Globals are now compiled into the resources
        expected_changes = [
            "Environment.Variables",
            "Environment.Variables.QUEUE_URL",
            "Environment.Variables.QUEUE_URL.Fn::If",
            "VpcConfig.SecurityGroupIds",
            "VpcConfig.SubnetIds",
        ]
        self.assertCountEqual(expected_changes, function_1_vertex.changed_attributes.keys())
        self.assertCountEqual(expected_changes, function_2_vertex.changed_attributes.keys())

        self.assertEqual("src/", function_1_vertex.attributes["CodeUri"])
        self.assertEqual("python3.9", function_1_vertex.attributes["Runtime"])
        self.assertEqual(5, function_1_vertex.attributes["Timeout"])
        self.assertEqual("Active", function_1_vertex.attributes["Tracing"])
        self.assertEqual("hello", function_1_vertex.attributes["Environment"]["Variables"]["NEW_VAR"])
        self.assertEqual("Production", function_1_vertex.attributes["Environment"]["Variables"]["STAGE"])
        self.assertEqual("resource-table", function_1_vertex.attributes["Environment"]["Variables"]["TABLE_NAME"])
        self.assertEqual(['sg-123', 'sg-456', 'sg-first'], function_1_vertex.attributes["VpcConfig"]["SecurityGroupIds"])
        self.assertEqual(['subnet-123', 'subnet-456'], function_1_vertex.attributes["VpcConfig"]["SubnetIds"])

        self.assertEqual("src/", function_2_vertex.attributes["CodeUri"])
        self.assertEqual("python3.8", function_2_vertex.attributes["Runtime"])
        self.assertEqual(5, function_2_vertex.attributes["Timeout"])
        self.assertEqual("Active", function_2_vertex.attributes["Tracing"])
        self.assertEqual("Production", function_2_vertex.attributes["Environment"]["Variables"]["STAGE"])
        self.assertEqual("global-table", function_2_vertex.attributes["Environment"]["Variables"]["TABLE_NAME"])
        self.assertEqual(['sg-123', 'sg-456'], function_2_vertex.attributes["VpcConfig"]["SecurityGroupIds"])
        self.assertEqual(['subnet-123', 'subnet-456'], function_2_vertex.attributes["VpcConfig"]["SubnetIds"])

        # check 'self' attribute is stored as 'self_'
        mapping_index = local_graph.vertices_block_name_map["mappings"]["ServiceDiscovery"][0]
        mapping_vertex = local_graph.vertices[mapping_index]

        attribute_dict = mapping_vertex.get_attribute_dict()
        self.assertNotIn("self", attribute_dict.keys())
        self.assertIn("self_", attribute_dict.keys())


    def test_encryption_aws(self):
        sam_file_path = Path(TEST_DIRNAME) / "resources/encryption/test.json"
        definitions, _ = create_definitions(root_folder="", files=[str(sam_file_path)], runner_filter=RunnerFilter())
        local_graph = CloudformationLocalGraph(definitions)
        local_graph._create_vertices()
        local_graph.calculate_encryption_attribute(ENCRYPTION_BY_RESOURCE_TYPE)
        all_attributes = [vertex.get_attribute_dict() for vertex in local_graph.vertices]
        for attribute_dict in all_attributes:
            [resource_type, resource_name] = attribute_dict[CustomAttributes.ID].split(".")
            if resource_type in ENCRYPTION_BY_RESOURCE_TYPE:
                is_encrypted = attribute_dict[CustomAttributes.ENCRYPTION]
                details = attribute_dict[CustomAttributes.ENCRYPTION_DETAILS]
                self.assertEqual(is_encrypted, EncryptionValues.ENCRYPTED.value if resource_name.startswith("Encrypted")
                                 else EncryptionValues.UNENCRYPTED.value, f'failed for "{resource_type}.{resource_name}"')
                if is_encrypted == EncryptionValues.ENCRYPTED.value:
                    attribute_dict_keys = '\t'.join(list(attribute_dict.keys()))
                    if 'KmsKeyId' in attribute_dict_keys or 'KMSMasterKeyId' in attribute_dict_keys:
                        self.assertEqual(details, EncryptionTypes.KMS_VALUE.value, f'Bad encryption details for "{resource_type}.{resource_name}"')
                    else:
                        self.assertIn(details, [EncryptionTypes.AES256.value, EncryptionTypes.KMS_VALUE.value, EncryptionTypes.NODE_TO_NODE.value, EncryptionTypes.DEFAULT_KMS.value], f'Bad encryption details for "{resource_type}.{resource_name}"')
                else:
                    self.assertEqual(details, "")
            else:
                self.assertIsNone(attribute_dict.get(CustomAttributes.ENCRYPTION))
                self.assertIsNone(attribute_dict.get(CustomAttributes.ENCRYPTION_DETAILS))
