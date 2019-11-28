import unittest

from bridgecrew.terraformscanner.models.enums import ScanResult
from bridgecrew.terraformscanner.scanner_registry import ScannerRegistry
from bridgecrew.terraformscanner.scanners import *

class TestScannerRegistry(unittest.TestCase):

    def test_num_of_scanners(self):
        registry = ScannerRegistry()
        scanners_counter = 0
        for key in list(registry.scanners.keys()):
            scanners_counter+=len(registry.scanners[key])

        self.assertEqual(scanners_counter,11)




if __name__ == '__main__':
    unittest.main()
