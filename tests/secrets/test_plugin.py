import unittest
from checkov.secrets.plugins.entropy_keyword_combinator import EntropyKeywordCombinator

class TestCombinatorPlugin(unittest.TestCase):

    def setUp(self) -> None:
        self.plugin = EntropyKeywordCombinator(4.5)

    def test_positive_value(self):
        result = self.plugin.analyze_line("mock.tf", "api_key = \"wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMAAAKEY\"", 5)
        self.assertEqual(1, len(result))
        secret = result.pop()
        self.assertEqual('Base64 High Entropy String', secret.type)
        self.assertEqual('c00f1a6e4b20aa64691d50781b810756d6254b8e', secret.secret_hash)

    def test_negative_keyword_value(self):
        result = self.plugin.analyze_line("mock.tf", "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMAAAKEY", 5)
        self.assertEqual(0, len(result))

    def test_negative_entropy_value(self):
        result = self.plugin.analyze_line("mock.tf", "api_key = var.api_key", 5)
        self.assertEqual(0, len(result))
