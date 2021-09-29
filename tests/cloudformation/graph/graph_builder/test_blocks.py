from unittest import TestCase

from checkov.cloudformation.graph_builder.graph_components.block_types import BlockType
from checkov.cloudformation.graph_builder.graph_components.blocks import CloudformationBlock


class TestBlocks(TestCase):
    def test_update_complex_key(self):
        config = {'labels': [{'app.kubernetes.io/name': '${local.name}', 'app.kubernetes.io/instance': 'hpa',
                              'app.kubernetes.io/version': '1.0.0', 'app.kubernetes.io/managed-by': 'terraform'}]}
        attributes = {'labels': {'app.kubernetes.io/name': '${local.name}', 'app.kubernetes.io/instance': 'hpa',
                                 'app.kubernetes.io/version': '1.0.0', 'app.kubernetes.io/managed-by': 'terraform'},
                      'labels.app.kubernetes.io/name': '${local.name}', 'labels.app.kubernetes.io/instance': 'hpa',
                      'labels.app.kubernetes.io/version': '1.0.0', 'labels.app.kubernetes.io/managed-by': 'terraform'}
        block = CloudformationBlock(name='test_local_name', config=config, path='', block_type=BlockType.RESOURCE,
                               attributes=attributes)

        block.update_attribute(attribute_key="labels.app.kubernetes.io/name", change_origin_id=0,
                                           attribute_value="dummy value", previous_breadcrumbs=[], attribute_at_dest="")
        self.assertEquals("dummy value", block.attributes["labels.app.kubernetes.io/name"])
