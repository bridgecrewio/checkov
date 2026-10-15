import unittest

from checkov.common.util.secrets import string_has_secrets, ALL, AWS, GENERAL, omit_secret_value_from_line, \
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

    # Regression for https://github.com/bridgecrewio/checkov/issues/7542
    def test_aws_secret_key_pattern_ignores_non_mixed_40_char_values(self):
        # Legitimate Lambda env values from the issue report (and similar resource names)
        # must not be treated as AWS secret access keys just because of length.
        false_positives = [
            "mdp/feature-logging/FdaCompositePipeline",  # 40-char namespace-like value
            "https://www.fda.gov/media/76860/download",  # 40-char URL
            "mdp-test-new-destroy-147997161038-uploads-bucket",  # 48-char bucket name
            "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",  # 40 identical chars
            "abcdefghijklmnopqrstuvwxyzabcdefghijklmn",  # 40 lower-only
            "ABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMN",  # 40 upper-only
            "abcdefghijklmnopqrstuvwxyz0123456789abcd",  # lower+digit, no upper
        ]
        for value in false_positives:
            self.assertFalse(
                string_has_secrets(value, AWS),
                msg=f"unexpected AWS secret match for {value!r}",
            )

        # Real AWS secret access keys mix upper, lower, and digits within 40 base64 chars
        real_secret = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"  # checkov:skip=CKV_SECRET_6 test secret
        self.assertTrue(string_has_secrets(real_secret, AWS))
        self.assertTrue(get_secrets_from_string(real_secret, AWS))

