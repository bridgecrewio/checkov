import os
import unittest

from checkov.common.checks_infra.resource_attribute_filters import attribute_resources
from checkov.common.checks_infra import special_attributes


class TestAttributeResourceTypes(unittest.TestCase):
    def test_attribute_resource_type_loading(self):
        expected = {
            'tags': ['aws', 'azure'],
            'Tags': ['aws'],
            'labels': ['gcp']
        }

        for attr, providers in expected.items():
            self.assertIn(attr, attribute_resources)
            for provider in providers + ['__all__']:
                self.assertIn(provider, attribute_resources[attr])

    def test_get_attribute_resource_types(self):
        self.assertIsNone(special_attributes.get_attribute_resource_types({}))
        self.assertIsNone(special_attributes.get_attribute_resource_types({'attribute': 'abc'}))
        self.assertIsNotNone(special_attributes.get_attribute_resource_types({'attribute': 'labels'}))
        self.assertIsNotNone(special_attributes.get_attribute_resource_types({'attribute': 'tags'}))
        self.assertIsNotNone(special_attributes.get_attribute_resource_types({'attribute': 'Tags'}))
        self.assertIsNotNone(special_attributes.get_attribute_resource_types({'attribute': 'tags.owner'}))
        self.assertIsNotNone(special_attributes.get_attribute_resource_types({'attribute': 'labels.owner'}))
        self.assertIsNotNone(special_attributes.get_attribute_resource_types({'attribute': 'Tags.Key'}))
        self.assertIsNotNone(special_attributes.get_attribute_resource_types({'attribute': 'labels'}, provider='gcp'))
        self.assertIsNotNone(special_attributes.get_attribute_resource_types({'attribute': 'tags'}, provider='aws'))
        self.assertIsNotNone(special_attributes.get_attribute_resource_types({'attribute': 'tags'}, provider='azure'))
        self.assertIsNotNone(special_attributes.get_attribute_resource_types({'attribute': 'Tags'}, provider='aws'))
        self.assertIsNone(special_attributes.get_attribute_resource_types({'attribute': 'labels'}, provider='aws'))
        self.assertIsNone(special_attributes.get_attribute_resource_types({'attribute': 'tags'}, provider='gcp'))
        self.assertIsNone(special_attributes.get_attribute_resource_types({'attribute': 'Tags'}, provider='gcp'))
        self.assertTrue(any(r for r in special_attributes.get_attribute_resource_types({'attribute': 'tags'}) if r.startswith('aws')))
        self.assertTrue(any(r for r in special_attributes.get_attribute_resource_types({'attribute': 'tags'}, provider='aws') if r.startswith('aws')))
        self.assertFalse(any(r for r in special_attributes.get_attribute_resource_types({'attribute': 'tags'}, provider='aws') if r.startswith('azure')))
        self.assertTrue(any(r for r in special_attributes.get_attribute_resource_types({'attribute': 'tags'}) if r.startswith('azure')))
        self.assertTrue(any(r for r in special_attributes.get_attribute_resource_types({'attribute': 'tags'}, provider='azure') if r.startswith('azure')))
        self.assertFalse(any(r for r in special_attributes.get_attribute_resource_types({'attribute': 'tags'}, provider='azure') if r.startswith('aws')))

