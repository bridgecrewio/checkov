import os
import unittest

from unittest import mock



class TestBCApiUrl(unittest.TestCase):

    @mock.patch.dict(os.environ,{'BC_API_URL':'foo'})
    def test_overriding_bc_api_url(self):
        from checkov.common.bridgecrew.platform_integration import BC_API_URL
        self.assertEqual(BC_API_URL,"foo")


if __name__ == '__main__':
    unittest.main()
