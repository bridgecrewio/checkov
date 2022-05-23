import unittest

from checkov.common.bridgecrew.severities import get_highest_severity_below_level, BcSeverities


class TestSeverities(unittest.TestCase):

    def test_get_highest_severity_below_level(self):
        self.assertEqual(get_highest_severity_below_level(2).name, BcSeverities.LOW)
        self.assertEqual(get_highest_severity_below_level(4).name, BcSeverities.HIGH)
        self.assertEqual(get_highest_severity_below_level(42).name, BcSeverities.CRITICAL)
        self.assertIsNone(get_highest_severity_below_level(0))


if __name__ == '__main__':
    unittest.main()
