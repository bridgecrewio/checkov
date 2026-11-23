import base64
import random
import string
import time
import unittest

from checkov.common.util.secrets import string_has_secrets, ALL, AWS, AZURE, GENERAL, omit_secret_value_from_line, \
    get_secrets_from_string


class TestSecrets(unittest.TestCase):

    def test_secrets(self):
        test_strings = [
            'AKIAIOSFODNN7EXAMPLE',  # checkov:skip=CKV_SECRET_2 test secret
            'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',  # checkov:skip=CKV_SECRET_6 test secret
            '-----BEGIN RSA PRIVATE KEY-----\n',  # checkov:skip=CKV_SECRET_13 test secret
            'Hello from Bridgecrew',
            'cert-manager.io/secret: org/repo',
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
        secret = 'AKIAIOSFODNN7EXAMPLE'  # checkov:skip=CKV_SECRET_6 test secret
        line = 'access_key: "AKIAIOSFODNN7EXAMPLE"'

        censored_line = omit_secret_value_from_line(secret, line)

        self.assertEqual(censored_line, 'access_key: "AKIAI**********"')

    def test_omit_none_secret_from_line(self):
        line = 'text'
        self.assertEqual(line, omit_secret_value_from_line(secret=None, line_text=line))

    def test_omit_non_string_secret_from_line(self):
        line = 'text'
        secret = True

        self.assertEqual(line, omit_secret_value_from_line(secret, line))

    def test_omit_long_secret_value_from_line(self):
        secret = '123456AKIAIOSFODNN7EXAMPLEAKIAIOSFODNN7EXAMPLEAKIAIOSFODNN7EXAM'  # checkov:skip=CKV_SECRET_6 test secret
        line = 'access_key: "123456AKIAIOSFODNN7EXAMPLEAKIAIOSFODNN7EXAMPLEAKIAIOSFODNN7EXAM"'

        censored_line = omit_secret_value_from_line(secret, line)

        self.assertEqual(censored_line, 'access_key: "123456**********"')

    def test_get_secrets_from_secrets(self):
        s = 'access_key: "AKIAIOSFODNN7EXAMPLE"'

        secret = get_secrets_from_string(s)

        assert secret == ["AKIAIOSFODNN7EXAMPLE"]

    def test_azure_hostnames_are_detected(self):
        test_strings = [
            'https://myaccount.blob.core.windows.net/container',
            'Server=tcp:mydb.database.windows.net,1433',
            'login via example.onmicrosoft.com',
            "'svc.servicebus.windows.net'",
            'endpoint: myapp.cloudapp.azure.com',
            'db.documents.azure.com',
        ]

        for s in test_strings:
            with self.subTest(s=s):
                self.assertTrue(string_has_secrets(s, AZURE))

    def test_azure_hostname_without_subdomain_is_not_detected(self):
        self.assertFalse(string_has_secrets('blob.core.windows.net', AZURE))
        self.assertFalse(string_has_secrets('no azure host here', AZURE))

    def test_get_secrets_from_string_returns_azure_hostname(self):
        s = 'url = "https://myaccount.blob.core.windows.net/container"'

        secrets = get_secrets_from_string(s, AZURE)

        self.assertEqual(secrets, ['myaccount.blob.core.windows.net'])

    def test_long_strings_without_azure_hostname_are_evaluated_quickly(self):
        rng = random.Random(0)
        # base64 and alphanumeric input contain no '.', so none of the Azure hostname patterns can match
        test_strings = {
            'base64': base64.b64encode(rng.randbytes(12_321)).decode(),
            'alphanumeric': ''.join(rng.choices(string.ascii_letters + string.digits, k=16_428)),
        }

        for name, s in test_strings.items():
            with self.subTest(input=name):
                start = time.monotonic()
                result = string_has_secrets(s, AZURE, GENERAL)
                elapsed = time.monotonic() - start

                self.assertFalse(result)
                self.assertLess(elapsed, 2)
