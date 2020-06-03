import unittest

from checkov.cloudformation.checks.resource.registry import resource_registry as registry


class TestScannerRegistry(unittest.TestCase):

    def test_num_of_scanners(self):
        scanners_counter = 0
        for key in list(registry.checks.keys()):
            scanners_counter += len(registry.checks[key])

        self.assertGreater(scanners_counter, 1)

    def test_non_colliding_check_ids(self):
        check_id_check_class_map = {}
        for (resource_type, checks) in registry.checks.items():
            for check in checks:
                check_id_check_class_map.setdefault(check.id, []).append(check)

        for check_id, check_classes in check_id_check_class_map.items():
            self.assertEqual(len(set(check_classes)), 1)


if __name__ == '__main__':
    unittest.main()
