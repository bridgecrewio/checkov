import unittest

from checkov.terraform.checks.provider.openstack.credentials import check
from checkov.common.models.enums import CheckResult


class TestCredentials(unittest.TestCase):

    def test_success(self):
        provider_conf = {'region': ['RegionOne'], 'auth_url': ["http://myauthurl:5000/v2.0"]}

        scan_result = check.scan_provider_conf(conf=provider_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)
        provider_conf = {}

        scan_result = check.scan_provider_conf(conf=provider_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_failure(self):
        provider_conf = {'region': ['RegionOne'], 'auth_url': ["http://myauthurl:5000/v2.0"], 'password': ['Ahngak0fuokeexee5Quiu0oohayeiXie']}
        scan_result = check.scan_provider_conf(conf=provider_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)
        provider_conf = {'region': ['RegionOne'], 'auth_url': ["http://myauthurl:5000/v2.0"], 'token': ['ifahghau4nun7eirahJ5baa8cichex7l']}
        scan_result = check.scan_provider_conf(conf=provider_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)
        provider_conf = {'region': ['RegionOne'], 'auth_url': ["http://myauthurl:5000/v2.0"], 'application_credential_secret': ['mie8siw5ooTaed0AeQuepeiGhah9xaif']}
        scan_result = check.scan_provider_conf(conf=provider_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

        if __name__ == '__main__':
            unittest.main()
