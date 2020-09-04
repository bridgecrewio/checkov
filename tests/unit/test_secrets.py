import os
import unittest

from checkov.common.util.secrets import *


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
        self.assertEqual(2, sum(1 for s in test_strings if string_has_secrets(s, 'aws')))

        # check two categories
        self.assertEqual(3, sum(1 for s in test_strings if string_has_secrets(s, 'aws', 'general')))

        # check explicit all
        self.assertEqual(3, sum(1 for s in test_strings if string_has_secrets(s, 'all')))

        # check explicit all plus another category
        self.assertEqual(3, sum(1 for s in test_strings if string_has_secrets(s, 'all', 'aws')))
