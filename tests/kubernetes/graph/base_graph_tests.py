from copy import deepcopy
from unittest import TestCase

from checkov.common.graph.graph_builder.graph_components.block_types import BlockType
from checkov.kubernetes.graph_builder.graph_components.blocks import KubernetesBlock


class TestGraph(TestCase):
    def assert_vertex(self, resource_vertex, resource):
        resource_name = f'{resource["kind"]}.{resource["metadata"].get("namespace", "default")}.{resource["metadata"]["name"]}'
        config = deepcopy(resource)
        attributes = deepcopy(config)
        enrich_attributes(attributes, resource)

        self.assertEqual(resource_name, resource_vertex.name)
        self.assertEqual(resource_name, resource_vertex.id)
        self.assertEqual(BlockType.RESOURCE, resource_vertex.block_type)
        self.assertEqual("Kubernetes", resource_vertex.source)
        self.assertDictEqual(config, resource_vertex.config)
        self.assertDictEqual(attributes, resource_vertex.attributes)


def extract_inner_attributes(attributes):
    attributes_to_add = {}
    for attribute_key in attributes:
        attribute_value = attributes[attribute_key]
        if isinstance(attribute_value, dict) or (
                isinstance(attribute_value, list) and len(attribute_value) > 0 and isinstance(attribute_value[0],
                                                                                              dict)):
            inner_attributes = KubernetesBlock.get_inner_attributes(attribute_key, attribute_value)
            attributes_to_add.update(inner_attributes)
    return attributes_to_add


def enrich_attributes(attributes, resource):
    attributes["resource_type"] = resource["kind"]
    attributes["__startline__"] = resource["__startline__"]
    attributes["__endline__"] = resource["__endline__"]
    attributes.update(extract_inner_attributes(attributes))
