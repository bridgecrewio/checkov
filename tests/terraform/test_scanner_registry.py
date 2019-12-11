import unittest

from checkov.terraform.checks.resource.registry import Registry


class TestScannerRegistry(unittest.TestCase):

    def test_num_of_scanners(self):
        registry = Registry()
        scanners_counter = 0
        for key in list(registry.checks.keys()):
            scanners_counter += len(registry.checks[key])

        self.assertGreater(scanners_counter, 1)


if __name__ == '__main__':
    unittest.main()
