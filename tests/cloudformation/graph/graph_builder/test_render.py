import os
from unittest.case import TestCase

from checkov.cloudformation.graph_builder.graph_components.block_types import BlockType
from checkov.cloudformation.graph_manager import CloudformationGraphManager

TEST_DIRNAME = os.path.dirname(os.path.realpath(__file__))


class TestRenderer(TestCase):
    def setUp(self) -> None:
        os.environ['UNIQUE_TAG'] = ''
        os.environ['RENDER_ASYNC_MAX_WORKERS'] = '50'
        os.environ['RENDER_VARIABLES_ASYNC'] = 'False'

    def test_render_ref(self):
        relative_path = './resources/variable_rendering/render_ref/'
        yaml_test_dir = os.path.realpath(os.path.join(TEST_DIRNAME, relative_path, 'yaml'))
        json_test_dir = os.path.realpath(os.path.join(TEST_DIRNAME, relative_path, 'json'))
        self.validate_render_ref(yaml_test_dir)
        self.validate_render_ref(json_test_dir)

    def validate_render_ref(self, test_dir: str):
        graph_manager = CloudformationGraphManager('acme', ['acme'])
        local_graph, _ = graph_manager.build_graph_from_source_directory(test_dir, render_variables=True)

        db_name_default_value = "db1"

        kms_master_key_id_expected_attributes = {'Default': None}
        db_name_expected_attributes = {'Default': db_name_default_value}
        my_source_queue_expected_attributes = {'KmsMasterKeyId.Ref': 'KmsMasterKeyId'}
        my_db_expected_attributes = {'DBName': db_name_default_value}
        my_db_instance_name_expected_attributes = {'Value.Ref': 'MyDB'}

        self.compare_vertex_attributes(local_graph, kms_master_key_id_expected_attributes, BlockType.PARAMETERS, 'KmsMasterKeyId')
        self.compare_vertex_attributes(local_graph, db_name_expected_attributes, BlockType.PARAMETERS, 'DBName')
        self.compare_vertex_attributes(local_graph, my_source_queue_expected_attributes, BlockType.RESOURCE, 'AWS::SQS::Queue.MySourceQueue')
        self.compare_vertex_attributes(local_graph, my_db_expected_attributes, BlockType.RESOURCE, 'AWS::RDS::DBInstance.MyDB')
        self.compare_vertex_attributes(local_graph, my_db_instance_name_expected_attributes, BlockType.OUTPUTS, 'MyDBInstanceName')

    def test_render_findinmap(self):
        relative_path = './resources/variable_rendering/render_findinmap/'
        yaml_test_dir = os.path.realpath(os.path.join(TEST_DIRNAME, relative_path, 'yaml'))
        json_test_dir = os.path.realpath(os.path.join(TEST_DIRNAME, relative_path, 'json'))
        self.validate_render_findinmap(yaml_test_dir)
        self.validate_render_findinmap(json_test_dir)

    def validate_render_findinmap(self, test_dir: str):
        graph_manager = CloudformationGraphManager('acme', ['acme'])
        local_graph, _ = graph_manager.build_graph_from_source_directory(test_dir, render_variables=True)

        region_map_expected_ami_value = "ami-0ff8a91507f77f867"

        region_map_expected_attributes = {'us-east-1.AMI': region_map_expected_ami_value}
        ec2instance_expected_attributes = {'ImageId': region_map_expected_ami_value}

        self.compare_vertex_attributes(local_graph, region_map_expected_attributes, BlockType.MAPPINGS, 'RegionMap')
        self.compare_vertex_attributes(local_graph, ec2instance_expected_attributes, BlockType.RESOURCE, 'AWS::EC2::Instance.EC2Instance')

    def test_render_getatt(self):
        relative_path = './resources/variable_rendering/render_getatt/'
        yaml_test_dir = os.path.realpath(os.path.join(TEST_DIRNAME, relative_path, 'yaml'))
        json_test_dir = os.path.realpath(os.path.join(TEST_DIRNAME, relative_path, 'json'))
        self.validate_render_getatt(yaml_test_dir)
        self.validate_render_getatt(json_test_dir)

    def validate_render_getatt(self, test_dir: str):
        graph_manager = CloudformationGraphManager('acme', ['acme'])
        local_graph, _ = graph_manager.build_graph_from_source_directory(test_dir, render_variables=True)

        web_vpc_expected_cidr_block = "172.16.0.0/16"

        web_vpc_expected_attributes = {'CidrBlock': web_vpc_expected_cidr_block}
        my_sg_expected_attributes = {'SecurityGroupIngress.CidrIp': web_vpc_expected_cidr_block}
        web_vpc_default_sg_expected_attributes = {'Value.Fn::GetAtt': ['WebVPC', 'DefaultSecurityGroup']}

        self.compare_vertex_attributes(local_graph, web_vpc_expected_attributes, BlockType.RESOURCE, 'AWS::EC2::VPC.WebVPC')
        self.compare_vertex_attributes(local_graph, my_sg_expected_attributes, BlockType.RESOURCE, 'AWS::EC2::SecurityGroup.MySG')
        self.compare_vertex_attributes(local_graph, web_vpc_default_sg_expected_attributes, BlockType.OUTPUTS, 'WebVPCDefaultSg')

    def test_render_sub(self):
        relative_path = './resources/variable_rendering/render_sub/'
        yaml_test_dir = os.path.realpath(os.path.join(TEST_DIRNAME, relative_path, 'yaml'))
        json_test_dir = os.path.realpath(os.path.join(TEST_DIRNAME, relative_path, 'json'))
        self.validate_render_sub(yaml_test_dir)
        self.validate_render_sub(json_test_dir)

    def validate_render_sub(self, test_dir: str):
        graph_manager = CloudformationGraphManager('acme', ['acme'])
        local_graph, _ = graph_manager.build_graph_from_source_directory(test_dir, render_variables=True)

        company_name_expected_value = "acme"
        web_vpc_expected_cidr_block = "172.16.0.0/16"

        # Parameters
        company_name_expected_attributes = {'Default': company_name_expected_value}
        environment_expected_attributes = {'Default': None}
        # Resources
        web_vpc_expected_attributes = {'CidrBlock': web_vpc_expected_cidr_block}
        default_db_expected_attributes = {'DBName': f"rds-${{AWS::AccountId}}-{company_name_expected_value}-${{Environment}}"}
        # Outputs
        db_endpoint_sg_expected_attributes = {'Value.Fn::Sub': "${DefaultDB.Endpoint.Address}:${DefaultDB.Endpoint.Port}"}
        web_vpc_cidr_block_expected_attributes = {'Value': web_vpc_expected_cidr_block}
        cidr_block_associations_expected_attributes = {'Value.Fn::Sub': "${WebVPC.CidrBlockAssociations}"}
        default_db_name_expected_attributes = {'Value': f"rds-${{AWS::AccountId}}-{company_name_expected_value}-${{Environment}}"}

        self.compare_vertex_attributes(local_graph, company_name_expected_attributes, BlockType.PARAMETERS, 'CompanyName')
        self.compare_vertex_attributes(local_graph, environment_expected_attributes, BlockType.PARAMETERS, 'Environment')
        self.compare_vertex_attributes(local_graph, web_vpc_expected_attributes, BlockType.RESOURCE, 'AWS::EC2::VPC.WebVPC')
        self.compare_vertex_attributes(local_graph, default_db_expected_attributes, BlockType.RESOURCE, 'AWS::RDS::DBInstance.DefaultDB')
        self.compare_vertex_attributes(local_graph, db_endpoint_sg_expected_attributes, BlockType.OUTPUTS, 'DBEndpoint')
        self.compare_vertex_attributes(local_graph, web_vpc_cidr_block_expected_attributes, BlockType.OUTPUTS, 'WebVPCCidrBlock')
        self.compare_vertex_attributes(local_graph, cidr_block_associations_expected_attributes, BlockType.OUTPUTS, 'CidrBlockAssociations')
        self.compare_vertex_attributes(local_graph, default_db_name_expected_attributes, BlockType.OUTPUTS, 'DefaultDBName')

    def test_render_subsequent_evals(self):
        relative_path = './resources/variable_rendering/render_subsequent_evals/'
        yaml_test_dir = os.path.realpath(os.path.join(TEST_DIRNAME, relative_path, 'yaml'))
        json_test_dir = os.path.realpath(os.path.join(TEST_DIRNAME, relative_path, 'json'))
        self.validate_render_subsequent_evals(yaml_test_dir)
        self.validate_render_subsequent_evals(json_test_dir)

    def validate_render_subsequent_evals(self, test_dir: str):
        graph_manager = CloudformationGraphManager('acme', ['acme'])
        local_graph, _ = graph_manager.build_graph_from_source_directory(test_dir, render_variables=True)

        cidr_block_expected_expected_value = "172.16.0.0/16"

        cidr_block_expected_attributes = {'Default': cidr_block_expected_expected_value}
        web_vpc_expected_attributes = {'CidrBlock': cidr_block_expected_expected_value}
        my_sg_expected_attributes = {'SecurityGroupIngress.CidrIp': cidr_block_expected_expected_value}

        self.compare_vertex_attributes(local_graph, cidr_block_expected_attributes, BlockType.PARAMETERS, 'CidrBlock')
        self.compare_vertex_attributes(local_graph, web_vpc_expected_attributes, BlockType.RESOURCE, 'AWS::EC2::VPC.WebVPC')
        self.compare_vertex_attributes(local_graph, my_sg_expected_attributes, BlockType.RESOURCE, 'AWS::EC2::SecurityGroup.MySG')

    def compare_vertex_attributes(self, local_graph, expected_attributes, block_type, block_name):
        vertex = local_graph.vertices[local_graph.vertices_block_name_map[block_type][block_name][0]]
        print(f'breadcrumbs = {vertex.breadcrumbs}')
        vertex_attributes = vertex.get_attribute_dict()
        for attribute_key, expected_value in expected_attributes.items():
            actual_value = vertex_attributes.get(attribute_key)
            self.assertEqual(expected_value, actual_value, f'error during comparing {block_type} in attribute key: {attribute_key}')
