import unittest

from checkov.arm.registry import arm_resource_registry, arm_parameter_registry


class TestScannerRegistry(unittest.TestCase):

    def test_num_of_scanners(self):
        resource_scanners_counter = 0
        for key in list(arm_resource_registry.checks.keys()):
            resource_scanners_counter += len(arm_resource_registry.checks[key])

        self.assertGreater(resource_scanners_counter, 0)

        parameter_scanners_counter = 0
        for key in list(arm_parameter_registry.checks.keys()):
            parameter_scanners_counter += len(arm_parameter_registry.checks[key])

        self.assertGreater(parameter_scanners_counter, 0)

    def test_non_colliding_check_ids(self):
        check_id_check_class_map = {}
        for (resource_type, checks) in arm_resource_registry.checks.items():
            for check in checks:
                check_id_check_class_map.setdefault(check.id, []).append(check)

        for (resource_type, checks) in arm_parameter_registry.checks.items():
            for check in checks:
                check_id_check_class_map.setdefault(check.id, []).append(check)

        for check_id, check_classes in check_id_check_class_map.items():
            self.assertEqual(len(set(check_classes)), 1)


if __name__ == '__main__':
    unittest.main()
