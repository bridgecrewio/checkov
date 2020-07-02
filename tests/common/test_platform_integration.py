import json
import os
import unittest
from unittest import mock

from urllib3_mock import Responses

from checkov.common.bridgecrew.platform_integration import BcPlatformIntegration

responses = Responses('requests.packages.urllib3')


class TestBCApiUrl(unittest.TestCase):

    @mock.patch.dict(os.environ, {'BC_API_URL': 'foo'})
    def test_overriding_bc_api_url(self):
        instance = BcPlatformIntegration()
        self.assertEqual(instance.bc_api_url, "foo")

    @mock.patch.dict(os.environ, {'BC_API_URL': 'http://test.invalid'})
    @responses.activate
    def test_guidelines_received(self):
        guideline1 = 'https://some.guideline.com/111'
        guideline2 = 'https://another.guideline.com/AWS/asdasd'

        def request_callback(_):
            resp_body = {'guidelines': {'CKV_AWS_1': guideline1, 'CKV_AWS_2': guideline2}}
            headers = {'Content-Type': 'application/json'}
            return 200, headers, json.dumps(resp_body)

        responses.add_callback('GET', '/guidelines',
                               callback=request_callback,
                               content_type='application/json')
        guidelines = BcPlatformIntegration().get_guidelines()
        self.assertTrue(isinstance(guidelines, dict))
        self.assertEqual(len(guidelines), 2)
        self.assertEqual(guidelines['CKV_AWS_1'], guideline1)
        self.assertEqual(guidelines['CKV_AWS_2'], guideline2)

    @mock.patch.dict(os.environ, {'BC_API_URL': 'http://test.invalid'})
    def test_guidelines_not_received(self):
        guidelines = BcPlatformIntegration().get_guidelines()
        self.assertEqual(guidelines, {})

    def test_real_guidelines(self):
        guidelines = BcPlatformIntegration().get_guidelines()
        self.assertGreater(len(guidelines.keys()), 0)


if __name__ == '__main__':
    unittest.main()
