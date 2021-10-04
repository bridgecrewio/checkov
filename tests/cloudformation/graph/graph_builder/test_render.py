import os
from unittest.case import TestCase

from checkov.cloudformation.graph_builder.graph_components.block_types import BlockType
from checkov.cloudformation.graph_manager import CloudformationGraphManager
from checkov.common.graph.db_connectors.networkx.networkx_db_connector import NetworkxConnector

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
        self.validate_render_ref(yaml_test_dir, 'yaml')
        self.validate_render_ref(json_test_dir, 'json')

    def validate_render_ref(self, test_dir: str, file_ext: str):
        graph_manager = CloudformationGraphManager(db_connector=NetworkxConnector())
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

        kms_master_key_id_expected_breadcrumbs = {}
        db_name_expected_breadcrumbs = {}
        my_source_queue_expected_breadcrumbs = {}
        my_db_expected_breadcrumbs = {'DBName': [{'type': BlockType.PARAMETERS, 'name': 'DBName', 'path': os.path.join(test_dir, f'test.{file_ext}'), 'attribute_key': 'Default'}]}
        my_db_instance_name_expected_breadcrumbs = {}

        self.compare_vertex_breadcrumbs(local_graph, kms_master_key_id_expected_breadcrumbs, BlockType.PARAMETERS, 'KmsMasterKeyId')
        self.compare_vertex_breadcrumbs(local_graph, db_name_expected_breadcrumbs, BlockType.PARAMETERS, 'DBName')
        self.compare_vertex_breadcrumbs(local_graph, my_source_queue_expected_breadcrumbs, BlockType.RESOURCE, 'AWS::SQS::Queue.MySourceQueue')
        self.compare_vertex_breadcrumbs(local_graph, my_db_expected_breadcrumbs, BlockType.RESOURCE, 'AWS::RDS::DBInstance.MyDB')
        self.compare_vertex_breadcrumbs(local_graph, my_db_instance_name_expected_breadcrumbs, BlockType.OUTPUTS, 'MyDBInstanceName')


    def test_render_findinmap(self):
        relative_path = './resources/variable_rendering/render_findinmap/'
        yaml_test_dir = os.path.realpath(os.path.join(TEST_DIRNAME, relative_path, 'yaml'))
        json_test_dir = os.path.realpath(os.path.join(TEST_DIRNAME, relative_path, 'json'))
        self.validate_render_findinmap(yaml_test_dir, 'yaml')
        self.validate_render_findinmap(json_test_dir, 'json')

    def validate_render_findinmap(self, test_dir: str, file_ext: str):
        graph_manager = CloudformationGraphManager(db_connector=NetworkxConnector())
        local_graph, _ = graph_manager.build_graph_from_source_directory(test_dir, render_variables=True)

        region_map_expected_ami_value = "ami-0ff8a91507f77f867"

        region_map_expected_attributes = {'us-east-1.AMI': region_map_expected_ami_value}
        ec2instance_expected_attributes = {'ImageId': region_map_expected_ami_value}

        self.compare_vertex_attributes(local_graph, region_map_expected_attributes, BlockType.MAPPINGS, 'RegionMap')
        self.compare_vertex_attributes(local_graph, ec2instance_expected_attributes, BlockType.RESOURCE, 'AWS::EC2::Instance.EC2Instance')

        region_map_expected_breadcrumbs = {}
        ec2instance_expected_breadcrumbs = {'ImageId': [{'type': BlockType.MAPPINGS, 'name': 'RegionMap', 'path': os.path.join(test_dir, f'test.{file_ext}'), 'attribute_key': 'us-east-1.AMI'}]}

        self.compare_vertex_breadcrumbs(local_graph, region_map_expected_breadcrumbs, BlockType.MAPPINGS, 'RegionMap')
        self.compare_vertex_breadcrumbs(local_graph, ec2instance_expected_breadcrumbs, BlockType.RESOURCE, 'AWS::EC2::Instance.EC2Instance')


    def test_render_getatt(self):
        relative_path = './resources/variable_rendering/render_getatt/'
        yaml_test_dir = os.path.realpath(os.path.join(TEST_DIRNAME, relative_path, 'yaml'))
        json_test_dir = os.path.realpath(os.path.join(TEST_DIRNAME, relative_path, 'json'))
        self.validate_render_getatt(yaml_test_dir, 'yaml')
        self.validate_render_getatt(json_test_dir, 'json')

    def validate_render_getatt(self, test_dir: str, file_ext: str):
        graph_manager = CloudformationGraphManager(db_connector=NetworkxConnector())
        local_graph, _ = graph_manager.build_graph_from_source_directory(test_dir, render_variables=True)

        web_vpc_expected_cidr_block = "172.16.0.0/16"

        web_vpc_expected_attributes = {'CidrBlock': web_vpc_expected_cidr_block}
        my_sg_expected_attributes = {'SecurityGroupIngress.CidrIp': web_vpc_expected_cidr_block}
        web_vpc_default_sg_expected_attributes = {'Value.Fn::GetAtt': ['WebVPC', 'DefaultSecurityGroup']}

        self.compare_vertex_attributes(local_graph, web_vpc_expected_attributes, BlockType.RESOURCE, 'AWS::EC2::VPC.WebVPC')
        self.compare_vertex_attributes(local_graph, my_sg_expected_attributes, BlockType.RESOURCE, 'AWS::EC2::SecurityGroup.MySG')
        self.compare_vertex_attributes(local_graph, web_vpc_default_sg_expected_attributes, BlockType.OUTPUTS, 'WebVPCDefaultSg')

        web_vpc_expected_breadcrumbs = {}
        my_sg_expected_breadcrumbs = {'SecurityGroupIngress.CidrIp': [{'type': BlockType.RESOURCE, 'name': 'AWS::EC2::VPC.WebVPC', 'path': os.path.join(test_dir, f'test.{file_ext}'), 'attribute_key': 'CidrBlock'}]}
        web_vpc_default_sg_expected_breadcrumbs = {}

        self.compare_vertex_breadcrumbs(local_graph, web_vpc_expected_breadcrumbs, BlockType.RESOURCE, 'AWS::EC2::VPC.WebVPC')
        self.compare_vertex_breadcrumbs(local_graph, my_sg_expected_breadcrumbs, BlockType.RESOURCE, 'AWS::EC2::SecurityGroup.MySG')
        self.compare_vertex_breadcrumbs(local_graph, web_vpc_default_sg_expected_breadcrumbs, BlockType.OUTPUTS, 'WebVPCDefaultSg')

    def test_render_sub(self):
        relative_path = './resources/variable_rendering/render_sub/'
        yaml_test_dir = os.path.realpath(os.path.join(TEST_DIRNAME, relative_path, 'yaml'))
        json_test_dir = os.path.realpath(os.path.join(TEST_DIRNAME, relative_path, 'json'))
        self.validate_render_sub(yaml_test_dir, 'yaml')
        self.validate_render_sub(json_test_dir, 'json')

    def validate_render_sub(self, test_dir: str, file_ext: str):
        graph_manager = CloudformationGraphManager(db_connector=NetworkxConnector())
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

        company_name_expected_breadcrumbs = {}
        environment_expected_breadcrumbs = {}
        web_vpc_expected_breadcrumbs = {}
        default_db_expected_breadcrumbs = {'DBName': [{'type': BlockType.PARAMETERS, 'name': 'CompanyName', 'path': os.path.join(test_dir, f'test.{file_ext}'), 'attribute_key': 'Default'}]}
        db_endpoint_sg_expected_breadcrumbs = {}
        web_vpc_cidr_block_expected_breadcrumbs = {'Value': [{'type': BlockType.RESOURCE, 'name': 'AWS::EC2::VPC.WebVPC', 'path': os.path.join(test_dir, f'test.{file_ext}'), 'attribute_key': 'CidrBlock'}]}
        cidr_block_associations_expected_breadcrumbs = {}
        default_db_name_expected_breadcrumbs = {'Value': [{'type': BlockType.PARAMETERS, 'name': 'CompanyName', 'path': os.path.join(test_dir, f'test.{file_ext}'), 'attribute_key': 'Default'}]}

        self.compare_vertex_breadcrumbs(local_graph, company_name_expected_breadcrumbs, BlockType.PARAMETERS, 'CompanyName')
        self.compare_vertex_breadcrumbs(local_graph, environment_expected_breadcrumbs, BlockType.PARAMETERS, 'Environment')
        self.compare_vertex_breadcrumbs(local_graph, web_vpc_expected_breadcrumbs, BlockType.RESOURCE, 'AWS::EC2::VPC.WebVPC')
        self.compare_vertex_breadcrumbs(local_graph, default_db_expected_breadcrumbs, BlockType.RESOURCE, 'AWS::RDS::DBInstance.DefaultDB')
        self.compare_vertex_breadcrumbs(local_graph, db_endpoint_sg_expected_breadcrumbs, BlockType.OUTPUTS, 'DBEndpoint')
        self.compare_vertex_breadcrumbs(local_graph, web_vpc_cidr_block_expected_breadcrumbs, BlockType.OUTPUTS, 'WebVPCCidrBlock')
        self.compare_vertex_breadcrumbs(local_graph, cidr_block_associations_expected_breadcrumbs, BlockType.OUTPUTS, 'CidrBlockAssociations')
        self.compare_vertex_breadcrumbs(local_graph, default_db_name_expected_breadcrumbs, BlockType.OUTPUTS, 'DefaultDBName')


    def test_render_subsequent_evals(self):
        relative_path = './resources/variable_rendering/render_subsequent_evals/'
        yaml_test_dir = os.path.realpath(os.path.join(TEST_DIRNAME, relative_path, 'yaml'))
        json_test_dir = os.path.realpath(os.path.join(TEST_DIRNAME, relative_path, 'json'))
        self.validate_render_subsequent_evals(yaml_test_dir, 'yaml')
        self.validate_render_subsequent_evals(json_test_dir, 'json')

    def validate_render_subsequent_evals(self, test_dir: str, file_ext: str):
        graph_manager = CloudformationGraphManager(db_connector=NetworkxConnector())
        local_graph, _ = graph_manager.build_graph_from_source_directory(test_dir, render_variables=True)

        cidr_block_expected_expected_value = "172.16.0.0/16"

        cidr_block_expected_attributes = {'Default': cidr_block_expected_expected_value}
        web_vpc_expected_attributes = {'CidrBlock': cidr_block_expected_expected_value}
        my_sg_expected_attributes = {'SecurityGroupIngress.CidrIp': cidr_block_expected_expected_value}

        self.compare_vertex_attributes(local_graph, cidr_block_expected_attributes, BlockType.PARAMETERS, 'CidrBlock')
        self.compare_vertex_attributes(local_graph, web_vpc_expected_attributes, BlockType.RESOURCE, 'AWS::EC2::VPC.WebVPC')
        self.compare_vertex_attributes(local_graph, my_sg_expected_attributes, BlockType.RESOURCE, 'AWS::EC2::SecurityGroup.MySG')

        cidr_block_expected_breadcrumbs = {}
        web_vpc_expected_breadcrumbs = {'CidrBlock': [{'type': BlockType.PARAMETERS, 'name': 'CidrBlock', 'path': os.path.join(test_dir, f'test.{file_ext}'), 'attribute_key': 'Default'}, {'type': BlockType.RESOURCE, 'name': 'AWS::EC2::VPC.WebVPC', 'path': os.path.join(test_dir, f'test.{file_ext}'), 'attribute_key': 'CidrBlock'}]}
        my_sg_expected_breadcrumbs = {'SecurityGroupIngress.CidrIp': [{'type': BlockType.PARAMETERS, 'name': 'CidrBlock', 'path': os.path.join(test_dir, f'test.{file_ext}'), 'attribute_key': 'Default'}, {'type': BlockType.RESOURCE, 'name': 'AWS::EC2::VPC.WebVPC', 'path': os.path.join(test_dir, f'test.{file_ext}'), 'attribute_key': 'CidrBlock'}]}

        self.compare_vertex_breadcrumbs(local_graph, cidr_block_expected_breadcrumbs, BlockType.PARAMETERS, 'CidrBlock')
        self.compare_vertex_breadcrumbs(local_graph, web_vpc_expected_breadcrumbs, BlockType.RESOURCE, 'AWS::EC2::VPC.WebVPC')
        self.compare_vertex_breadcrumbs(local_graph, my_sg_expected_breadcrumbs, BlockType.RESOURCE, 'AWS::EC2::SecurityGroup.MySG')

    def test_render_select(self):
        relative_path = './resources/variable_rendering/render_select/'
        yaml_test_dir = os.path.realpath(os.path.join(TEST_DIRNAME, relative_path, 'yaml'))
        json_test_dir = os.path.realpath(os.path.join(TEST_DIRNAME, relative_path, 'json'))
        self.validate_render_select(yaml_test_dir, 'yaml')
        self.validate_render_select(json_test_dir, 'json')

    def validate_render_select(self, test_dir: str, file_ext: str):
        graph_manager = CloudformationGraphManager(db_connector=NetworkxConnector())
        local_graph, _ = graph_manager.build_graph_from_source_directory(test_dir, render_variables=True)

        subnet0_expected_attributes = {'CidrBlock': '10.0.48.0/24'}
        grapes_select_expected_attributes = {'Value': 'grapes'}
        out_of_bound_select_expected_attributes = {'Value.Fn::Select': ['7', ['apples', 'grapes', 'oranges', 'mangoes']]}

        self.compare_vertex_attributes(local_graph, subnet0_expected_attributes, BlockType.RESOURCE, 'AWS::EC2::Subnet.Subnet0')
        self.compare_vertex_attributes(local_graph, grapes_select_expected_attributes, BlockType.OUTPUTS, 'GrapesSelect')
        self.compare_vertex_attributes(local_graph, out_of_bound_select_expected_attributes, BlockType.OUTPUTS, 'OutOfBoundSelect')

        subnet0_expected_breadcrumbs = {'CidrBlock.Fn::Select.1': [{'type': BlockType.PARAMETERS, 'name': 'DbSubnetIpBlocks', 'path': os.path.join(test_dir, f'test.{file_ext}'), 'attribute_key': 'Default'}], 'CidrBlock.Fn::Select': [{'type': BlockType.PARAMETERS, 'name': 'DbSubnetIpBlocks', 'path': os.path.join(test_dir, f'test.{file_ext}'), 'attribute_key': 'Default'}]}
        grapes_select_expected_breadcrumbs = {}
        out_of_bound_select_expected_breadcrumbs = {}

        self.compare_vertex_breadcrumbs(local_graph, subnet0_expected_breadcrumbs, BlockType.RESOURCE, 'AWS::EC2::Subnet.Subnet0')
        self.compare_vertex_breadcrumbs(local_graph, grapes_select_expected_breadcrumbs, BlockType.OUTPUTS, 'GrapesSelect')
        self.compare_vertex_breadcrumbs(local_graph, out_of_bound_select_expected_breadcrumbs, BlockType.OUTPUTS, 'OutOfBoundSelect')

    def test_render_join(self):
        relative_path = './resources/variable_rendering/render_join/'
        yaml_test_dir = os.path.realpath(os.path.join(TEST_DIRNAME, relative_path, 'yaml'))
        json_test_dir = os.path.realpath(os.path.join(TEST_DIRNAME, relative_path, 'json'))
        self.validate_render_join(yaml_test_dir, 'yaml')
        self.validate_render_join(json_test_dir, 'json')

    def validate_render_join(self, test_dir: str, file_ext: str):
        graph_manager = CloudformationGraphManager(db_connector=NetworkxConnector())
        local_graph, _ = graph_manager.build_graph_from_source_directory(test_dir, render_variables=True)

        s3bucket1_expected_attributes = {'BucketName': 'a:b:c'}
        s3bucket2_expected_attributes = {'BucketName': 'my_bucket_name_test'}

        self.compare_vertex_attributes(local_graph, s3bucket1_expected_attributes, BlockType.RESOURCE, 'AWS::S3::Bucket.S3Bucket1')
        self.compare_vertex_attributes(local_graph, s3bucket2_expected_attributes, BlockType.RESOURCE, 'AWS::S3::Bucket.S3Bucket2')

        s3bucket1_expected_breadcrumbs = {}
        s3bucket2_expected_breadcrumbs = {'BucketName.Fn::Join.1.0': [{'type': BlockType.PARAMETERS, 'name': 'BucketName', 'path': os.path.join(test_dir, f'test.{file_ext}'), 'attribute_key': 'Default'}], 'BucketName.Fn::Join.1': [{'type': BlockType.PARAMETERS, 'name': 'BucketName', 'path': os.path.join(test_dir, f'test.{file_ext}'), 'attribute_key': 'Default'}], 'BucketName.Fn::Join': [{'type': BlockType.PARAMETERS, 'name': 'BucketName', 'path': os.path.join(test_dir, f'test.{file_ext}'), 'attribute_key': 'Default'}]}

        self.compare_vertex_breadcrumbs(local_graph, s3bucket1_expected_breadcrumbs, BlockType.RESOURCE, 'AWS::S3::Bucket.S3Bucket1')
        self.compare_vertex_breadcrumbs(local_graph, s3bucket2_expected_breadcrumbs, BlockType.RESOURCE, 'AWS::S3::Bucket.S3Bucket2')

    def test_render_if(self):
        relative_path = './resources/variable_rendering/render_if/'
        yaml_test_dir = os.path.realpath(os.path.join(TEST_DIRNAME, relative_path, 'yaml'))
        json_test_dir = os.path.realpath(os.path.join(TEST_DIRNAME, relative_path, 'json'))
        self.valiate_render_if(yaml_test_dir, 'yaml')
        self.valiate_render_if(json_test_dir, 'json')

    def valiate_render_if(self, test_dir: str, file_ext: str):
        graph_manager = CloudformationGraphManager(db_connector=NetworkxConnector())
        local_graph, _ = graph_manager.build_graph_from_source_directory(test_dir, render_variables=True)

        ec2instance_expected_attributes = {'InstanceType': 'm1.large'}
        s3bucketsuspended_expected_attributes = {'VersioningConfiguration.Status': 'Suspended'}
        s3bucketenabled_expected_attributes = {'VersioningConfiguration.Status': 'Enabled'}

        self.compare_vertex_attributes(local_graph, ec2instance_expected_attributes, BlockType.RESOURCE, 'AWS::EC2::Instance.EC2Instance')
        self.compare_vertex_attributes(local_graph, s3bucketsuspended_expected_attributes, BlockType.RESOURCE, 'AWS::S3::Bucket.S3BucketSuspended')
        self.compare_vertex_attributes(local_graph, s3bucketenabled_expected_attributes, BlockType.RESOURCE, 'AWS::S3::Bucket.S3BucketEnabled')

        instancesize_breadcrumb = {'type': BlockType.PARAMETERS, 'name': 'InstanceSize', 'path': os.path.join(test_dir, f'test.{file_ext}'), 'attribute_key': 'Default'}
        ec2instance_expected_breadcrumbs = {
            'InstanceType.Fn::If.2.Fn::If.1': [instancesize_breadcrumb],
            'InstanceType.Fn::If.2.Fn::If': [instancesize_breadcrumb],
            'InstanceType.Fn::If.2': [instancesize_breadcrumb],
            'InstanceType.Fn::If': [instancesize_breadcrumb],
            'InstanceType': [instancesize_breadcrumb],
        }
        s3bucketsuspended_expected_breadcrumbs = {}
        s3bucketenabled_expected_breadcrumbs = {}

        self.compare_vertex_breadcrumbs(local_graph, ec2instance_expected_breadcrumbs, BlockType.RESOURCE, 'AWS::EC2::Instance.EC2Instance')
        self.compare_vertex_breadcrumbs(local_graph, s3bucketsuspended_expected_breadcrumbs, BlockType.RESOURCE, 'AWS::S3::Bucket.S3BucketSuspended')
        self.compare_vertex_breadcrumbs(local_graph, s3bucketenabled_expected_breadcrumbs, BlockType.RESOURCE, 'AWS::S3::Bucket.S3BucketEnabled')

    def compare_vertex_attributes(self, local_graph, expected_attributes, block_type, block_name):
        vertex = local_graph.vertices[local_graph.vertices_block_name_map[block_type][block_name][0]]
        vertex_attributes = vertex.get_attribute_dict()
        for attribute_key, expected_value in expected_attributes.items():
            actual_value = vertex_attributes.get(attribute_key)
            self.assertEqual(expected_value, actual_value, f'error during comparing {block_type} in attribute key: {attribute_key}')

    def compare_vertex_breadcrumbs(self, local_graph, expected_breadcrumbs, block_type, block_name):
        vertex = local_graph.vertices[local_graph.vertices_block_name_map[block_type][block_name][0]]
        vertex_breadcrumbs = vertex.breadcrumbs
        self.assertEqual(len(vertex_breadcrumbs), len(expected_breadcrumbs))
        if len(expected_breadcrumbs) > 0:
            for vertex_id, expected_value in expected_breadcrumbs.items():
                actual_value = vertex_breadcrumbs.get(vertex_id)
                self.assertEqual(expected_value, actual_value, f'actual breadcrumbs of vertex {vertex.id} different from'
                                                               f' expected. expected = {expected_breadcrumbs}'
                                                               f' and actual = {actual_value}')
