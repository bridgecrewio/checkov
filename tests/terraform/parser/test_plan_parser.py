import os
import unittest
from checkov.terraform.plan_parser import parse_tf_plan


class TestPlanFileParser(unittest.TestCase):

    def test_tags_values_are_flattened(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_plan_path = current_dir + "/resources/plan_tags/tfplan.json"
        tf_definitions, _ = parse_tf_plan(valid_plan_path)
        file_resource_definition = next(iter(tf_definitions.values()))['resource'][0]
        resource_definition = next(iter(file_resource_definition.values()))
        resource_attributes = next(iter(resource_definition.values()))
        resource_tags = resource_attributes['tags'][0]
        for tag_key, tag_value in resource_tags.items():
            if tag_key not in ['start_line', 'end_line']:
                self.assertIsInstance(tag_value, str)

    def test_more_tags_values_are_flattened(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_plan_path = current_dir + "/resources/plan_tags_variety/tfplan.json"
        tf_definitions, _ = parse_tf_plan(valid_plan_path)
        # TODO: this should also verify the flattening but at least shows it parses now.
        assert True

    def test_module_resources_have_unique_names(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_plan_path = current_dir + "/resources/plan_modules/tfplan.json"
        tf_definitions, _ = parse_tf_plan(valid_plan_path)
        resources = next(iter(tf_definitions.values()))['resource']
        unique_resource_names = set([resource_name for resource in resources
                          if 'null_resource' in resource.keys()
                          for resource_name in resource['null_resource'].keys()])
        assert len(unique_resource_names) == 3


if __name__ == '__main__':
    unittest.main()
