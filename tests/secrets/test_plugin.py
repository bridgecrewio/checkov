import unittest
from pathlib import Path

from checkov.secrets.plugins.entropy_keyword_combinator import EntropyKeywordCombinator


class TestCombinatorPlugin(unittest.TestCase):
    def setUp(self) -> None:
        self.plugin = EntropyKeywordCombinator()

    def test_positive_value(self):
        result = self.plugin.analyze_line("mock.tf", 'api_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMAAAKEY"', 5)
        self.assertEqual(1, len(result))
        secret = result.pop()
        self.assertEqual("Base64 High Entropy String", secret.type)
        self.assertEqual("c00f1a6e4b20aa64691d50781b810756d6254b8e", secret.secret_hash)

    def test_negative_keyword_value(self):
        result = self.plugin.analyze_line("mock.tf", "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMAAAKEY", 5)
        self.assertEqual(0, len(result))

    def test_negative_entropy_value(self):
        result = self.plugin.analyze_line("mock.tf", "api_key = var.api_key", 5)
        self.assertEqual(0, len(result))

    def test_popular_kubernetes_manifest_password(self):
        result = self.plugin.analyze_line("mock.yaml", 'pwd: "correcthorsebatterystaple"', 5)
        self.assertEqual(1, len(result))
        secret = result.pop()
        self.assertEqual("Base64 High Entropy String", secret.type)
        self.assertEqual("bfd3617727eab0e800e62a776c76381defbc4145", secret.secret_hash)

    def test_no_false_positive_py(self):
        # combinator plugin should ignore source code files
        result = self.plugin.analyze_line("main.py", 'api_key = "7T)G#dl5}c=T>kf$G3Bon^!R?kzF00"', 1)
        self.assertEqual(0, len(result))

    def test_no_false_positive_yml_1(self):
        test_file_path = Path(__file__).parent / "resources/cfn/secret-no-false-positive.yml"
        with open(file=str(test_file_path)) as f:
            for i, line in enumerate(f.readlines()):
                result = self.plugin.analyze_line("secret-no-false-positive.yml", line, i)
                self.assertEqual(0, len(result))
