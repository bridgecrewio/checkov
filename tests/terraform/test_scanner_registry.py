import unittest
from copy import deepcopy

# do not remove this - prevents circular import dependency
from checkov.common.bridgecrew.integration_features.features.policy_metadata_integration import integration as metadata_integration  # noqa

from checkov.common.checks_infra.checks_parser import GraphCheckParser
from checkov.common.checks_infra.registry import Registry
from checkov.terraform.checks.resource.registry import resource_registry as registry
from pathlib import Path

class TestScannerRegistry(unittest.TestCase):

    def setUp(self):
        self.checks = deepcopy(registry.checks)

    def tearDown(self) -> None:
        registry.checks = self.checks

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
            self.assertEqual(len(set(check_classes)), 1,"collision on check_id={}".format(check_id))

    def test_non_colliding_graph_check_ids(self):
        check_id_check_class_map = {}
        graph_registry = Registry(parser=GraphCheckParser(), checks_dir=str(Path(__file__).parent.parent.parent / "checkov" / "terraform" / "checks" / "graph_checks"))
        graph_registry.load_checks()
        for check in graph_registry.checks:
            check_id_check_class_map.setdefault(check.id, []).append(check)

        for check_id, check_classes in check_id_check_class_map.items():
            self.assertEqual(len(set(check_classes)), 1,"collision on check_id={}".format(check_id))


if __name__ == '__main__':
    unittest.main()
