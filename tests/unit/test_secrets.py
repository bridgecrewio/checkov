import unittest

from checkov.common.util.secrets import string_has_secrets, ALL, AWS, GENERAL, omit_secret_value_from_line, \
    get_secrets_from_string


class TestSecrets(unittest.TestCase):

    def test_secrets(self):
        test_strings = [
            'AKIAIOSFODNN7EXAMPLE',
            'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
            '-----BEGIN RSA PRIVATE KEY-----\n',
            'Hello from Bridgecrew'
        ]

        # check that no category checks all
        self.assertEqual(3, sum(1 for s in test_strings if string_has_secrets(s)))

        # check one category
        self.assertEqual(2, sum(1 for s in test_strings if string_has_secrets(s, AWS)))

        # check two categories
        self.assertEqual(3, sum(1 for s in test_strings if string_has_secrets(s, AWS, GENERAL)))

        # check explicit all
        self.assertEqual(3, sum(1 for s in test_strings if string_has_secrets(s, ALL)))

        # check explicit all plus another category
        self.assertEqual(3, sum(1 for s in test_strings if string_has_secrets(s, ALL, AWS)))

    # Regression test for https://github.com/bridgecrewio/checkov/issues/754
    def test_does_not_consider_single_hash_as_a_secret(self):
        # SHA1
        self.assertFalse(string_has_secrets("b5a5b36b6be8d98c6f1bea655536d67abef23be8"))

        # MD5
        self.assertFalse(string_has_secrets("d9de48cf0676e9edb99bd8ee1ed44a21"))

    def test_omit_secret_value_from_line(self):
        secret = 'AKIAIOSFODNN7EXAMPLE'
        line = 'access_key: "AKIAIOSFODNN7EXAMPLE"'

        censored_line = omit_secret_value_from_line(secret, line)

        self.assertEqual(censored_line, 'access_key: "AKIAI***************"')

    def test_get_secrets_from_secrets(self):
        s = 'access_key: "AKIAIOSFODNN7EXAMPLE"'

        secret = get_secrets_from_string(s)

        assert secret == ["AKIAIOSFODNN7EXAMPLE"]
