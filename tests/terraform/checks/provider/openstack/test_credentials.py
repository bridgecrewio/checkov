import unittest

import hcl2

from checkov.terraform.checks.provider.openstack.credentials import check
from checkov.common.models.enums import CheckResult


class TestCredentials(unittest.TestCase):
    def test_success_empty(self):
        hcl_res = hcl2.loads(
            """
            provider "openstack" {}
            """
        )
        provider_conf = hcl_res["provider"][0]["openstack"]
        scan_result = check.scan_provider_conf(conf=provider_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_region(self):
        hcl_res = hcl2.loads(
            """
            provider "openstack" {
                auth_url = "http://myauthurl:5000/v2.0"
                region   = "RegionOne"
            }
            """
        )
        provider_conf = hcl_res["provider"][0]["openstack"]
        scan_result = check.scan_provider_conf(conf=provider_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_failure_password(self):
        hcl_res = hcl2.loads(
            """
            provider "openstack" {
                auth_url = "http://myauthurl:5000/v2.0"
                region   = "RegionOne"
                password = "Ahngak0fuokeexee5Quiu0oohayeiXie"
            }
            """
        )
        provider_conf = hcl_res["provider"][0]["openstack"]
        scan_result = check.scan_provider_conf(conf=provider_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_token(self):
        hcl_res = hcl2.loads(
            """
            provider "openstack" {
                auth_url = "http://myauthurl:5000/v2.0"
                region   = "RegionOne"
                token    = "ifahghau4nun7eirahJ5baa8cichex7l"
            }
            """
        )
        provider_conf = hcl_res["provider"][0]["openstack"]
        scan_result = check.scan_provider_conf(conf=provider_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_app_secret(self):
        hcl_res = hcl2.loads(
            """
            provider "openstack" {
                auth_url = "http://myauthurl:5000/v2.0"
                region   = "RegionOne"
                application_credential_secret = "mie8siw5ooTaed0AeQuepeiGhah9xaif"
            }
            """
        )
        provider_conf = hcl_res["provider"][0]["openstack"]
        scan_result = check.scan_provider_conf(conf=provider_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)


if __name__ == "__main__":
    unittest.main()
