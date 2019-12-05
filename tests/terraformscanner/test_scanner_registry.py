import unittest

from checkov.terraform.checks.resource.registry import Registry


class TestScannerRegistry(unittest.TestCase):

    def test_num_of_scanners(self):
        registry = Registry()
        scanners_counter = 0
        for key in list(registry.scanners.keys()):
            scanners_counter+=len(registry.scanners[key])

        self.assertEqual(41,scanners_counter)




if __name__ == '__main__':
    unittest.main()
