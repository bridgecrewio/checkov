import unittest


class TestRegistry(unittest.TestCase):

    def setUp(self):
        from checkov.terraform.checks.data.registry import data_registry
        self.registry = data_registry

    def test_checks_loaded(self):
        self.assertGreater(len(self.registry.checks), 0)


if __name__ == '__main__':
    unittest.main()
