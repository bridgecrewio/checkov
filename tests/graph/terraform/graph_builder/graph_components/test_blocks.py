from unittest import TestCase

from checkov.terraform.graph_builder.graph_components.block_types import BlockType
from checkov.terraform.graph_builder.graph_components.blocks import Block


class TestBlocks(TestCase):
    def test_update_inner_attribute_1(self):
        config = {'aws_security_group': {'test': {'name': ['test'], 'vpc_id': ['${aws_vpc.vpc_main.id}'], 'tags': [{'Name': 'test'}],
                                                  'description': ['test - Elasticsearch Cluster'], 'ingress': [
                {'from_port': [443], 'to_port': [443], 'protocol': ['tcp'],
                 'security_groups': [['${aws_security_group.test.id}', '${data.aws_security_group.test.id}']]}]}}}

        block = Block(name='aws_security_group.test', config=config, path='test_path', block_type=BlockType.RESOURCE,
                      attributes=config['aws_security_group']['test'])

        block.update_inner_attribute(attribute_key='ingress.security_groups.0', nested_attributes=block.attributes, value_to_update='sg-0')
        block.update_inner_attribute(attribute_key='ingress.security_groups.1', nested_attributes=block.attributes, value_to_update='sg-1')

        self.assertEqual('sg-0', block.attributes['ingress.security_groups.0'],
                         f"failed to update ingress.security_groups.0, got {block.attributes['ingress.security_groups.0']}")
        self.assertEqual('sg-1', block.attributes['ingress.security_groups.1'],
                         f"failed to update ingress.security_groups.1, got {block.attributes['ingress.security_groups.1']}")
        self.assertEqual('sg-0', block.attributes['ingress']['security_groups'][0],
                         f"failed to update block.attributes['ingress']['security_groups'][0], got {block.attributes['ingress']['security_groups'][0]}")
        self.assertEqual('sg-1', block.attributes['ingress']['security_groups'][1],
                         f"failed to update block.attributes['ingress']['security_groups'][1], got {block.attributes['ingress']['security_groups'][1]}")

    def test_update_inner_attribute_2(self):
        config = {'aws_security_group': {'test': {'name': ['test'], 'vpc_id': ['${aws_vpc.vpc_main.id}'], 'ingress': [
            {'from_port': [53], 'to_port': [53], 'protocol': ['udp'], 'security_groups': [
                ['${data.test1.id}', '${data.test2.id}', '${data.test3.id}', '${data.test4.id}', '${data.test5.id}', '${data.test6.id}']],
             'cidr_blocks': [['test1', '${var.test2}', '${var.test4}']]}, {'from_port': [53], 'to_port': [53], 'protocol': ['tcp'], 'security_groups': [
                ['${data.test1.id}', '${data.test2.id}', '${data.test3.id}', '${data.test4.id}', '${data.test5.id}', '${data.test6.id}']],
                                                                           'cidr_blocks': [['test', '${var.test}', '${var.v3}']]}]}}}

        block = Block(name='aws_security_group.test', config=config, path='test_path', block_type=BlockType.RESOURCE,
                      attributes=config['aws_security_group']['test'])

        block.update_inner_attribute(attribute_key='ingress.0.cidr_blocks.1', nested_attributes=block.attributes, value_to_update='sg-1')

        self.assertEqual('sg-1', block.attributes['ingress.0.cidr_blocks.1'],
                         f"failed to update ingress.0.cidr_blocks.1, got {block.attributes['ingress.0.cidr_blocks.1']}")
        self.assertEqual('sg-1', block.attributes['ingress'][0]['cidr_blocks'][1],
                         f"failed to update block.attributes['ingress'][0]['cidr_blocks'][1], got {block.attributes['ingress'][0]['cidr_blocks'][1]}")

    def test_update_complex_key(self):
        config = {'labels': [{'app.kubernetes.io/name': '${local.name}', 'app.kubernetes.io/instance': 'hpa', 'app.kubernetes.io/version': '1.0.0', 'app.kubernetes.io/managed-by': 'terraform'}]}
        attributes = {'labels': {'app.kubernetes.io/name': '${local.name}', 'app.kubernetes.io/instance': 'hpa', 'app.kubernetes.io/version': '1.0.0', 'app.kubernetes.io/managed-by': 'terraform'}, 'labels.app.kubernetes.io/name': '${local.name}', 'labels.app.kubernetes.io/instance': 'hpa', 'labels.app.kubernetes.io/version': '1.0.0', 'labels.app.kubernetes.io/managed-by': 'terraform'}
        block = Block(name='test_local_name', config=config, path='', block_type=BlockType.LOCALS, attributes=attributes)

        err = block.update_inner_attribute(attribute_key="labels.app.kubernetes.io/name", nested_attributes=attributes,
                                           value_to_update="dummy value")
        self.assertEqual(None, err)

    def test_update_complex_key2(self):
        config = {'labels': [{'app.kubernetes.io/name': '${local.name}', 'app.kubernetes.io/instance': 'hpa',
                              'app.kubernetes.io/version': '1.0.0', 'app.kubernetes.io/managed-by': 'terraform'}]}
        attributes = {'var.owning_account': {'route_to': None, 'route_to_cidr_blocks': '${local.allowed_cidrs}',
                                             'static_routes': None, 'subnet_ids': '${local.own_vpc.private_subnet_ids}',
                                             'subnet_route_table_ids': '${local.own_vpc.private_route_table_ids}',
                                             'transit_gateway_vpc_attachment_id': None,
                                             'vpc_cidr': '${local.own_vpc.vpc_cidr}',
                                             'vpc_id': '${local.own_vpc.vpc_id}'}}
        block = Block(name='test_local_name', config=config, path='', block_type=BlockType.LOCALS,
                      attributes=attributes)
        value_to_update = [
            "${{'connected_accounts':'${var.connections}','eks':'${data.terraform_remote_state.eks}','existing_transit_gateway_id':'${module.transit_gateway.transit_gateway_id}','existing_transit_gateway_route_table_id':'${module.transit_gateway.transit_gateway_route_table_id}','expose_eks_sg':True,'vpcs':'${data.terraform_remote_state.vpc}'}[\"prod\"].outputs}"]
        err = block.update_inner_attribute(attribute_key="var.owning_account.vpc_cidr", nested_attributes=attributes,
                                           value_to_update=value_to_update)
        self.assertEqual(None, err)