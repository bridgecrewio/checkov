import os
import unittest

from checkov.terraform.plan_parser import parse_tf_plan


class TestPlanFileParser(unittest.TestCase):
    def test_tags_values_are_flattened(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_plan_path = current_dir + "/resources/plan_tags/tfplan.json"
        tf_definitions, _ = parse_tf_plan(valid_plan_path)
        file_resource_definition = next(iter(tf_definitions.values()))["resource"][0]
        resource_definition = next(iter(file_resource_definition.values()))
        resource_attributes = next(iter(resource_definition.values()))
        resource_tags = resource_attributes["tags"][0]
        for tag_key, tag_value in resource_tags.items():
            if tag_key not in ["start_line", "end_line"]:
                self.assertTrue(isinstance(tag_value, str))


if __name__ == "__main__":
    unittest.main()
