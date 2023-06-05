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

    def test_suspicious_keyword_no_secret(self):
        result = self.plugin.analyze_line("mock.json", "'wrong_one_time_password' = 'Du har tastet feil engangspassord'", 5)
        self.assertEqual(0, len(result))

    def test_suspicious_keyword_with_secret(self):
        result = self.plugin.analyze_line("mock.json", "'my_new_password':'F317a45xxmwov9bpgRhyuByXj2nxz7khS6yXQmfSaQCmwbTF1jpfgC56az4a'", 5)
        self.assertEqual(1, len(result))
        secret = result.pop()
        self.assertEqual("Base64 High Entropy String", secret.type)
        self.assertEqual("F317a45xxmwov9bpgRhyuByXj2nxz7khS6yXQmfSaQCmwbTF1jpfgC56az4a", secret.secret_value)

    def test_unquoted_secret(self):
        result = self.plugin.analyze_line("mock.yaml", 'export secret_access_key=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMAAAKEY', 5)
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

    def test_no_false_positive_yml_2(self):
        test_file_path = Path(__file__).parent / "resources/cfn/secret-no-false-positive2.yml"
        with open(file=str(test_file_path)) as f:
            for i, line in enumerate(f.readlines()):
                result = self.plugin.analyze_line("secret-no-false-positive2.yml", line, i)
                self.assertEqual(0, len(result))

    def test_no_false_positive_image_bytes(self):
        result = self.plugin.analyze_line("main.py", "'image/jpeg' : b'/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0a\nHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIy\nMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAACAAIDASIA\nAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQA\nAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3\nODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWm\np6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEA\nAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSEx\nBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElK\nU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3\nuLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD5/ooo\noAoo2Qoo'", 1)
        self.assertEqual(0, len(result))

    def test_no_false_positive_token(self):
        result = self.plugin.analyze_line("main.go", 'fmt.Sprintf("https://%s:%s@", token, token)', 1)
        self.assertEqual(0, len(result))

    def test_secret_value_in_keyword(self):
        result = self.plugin.analyze_line("mock.tf", 'export AWS_SECRET_ACCESS_KEY=h4t2TJheVRR8em5VdNCjrSJdQ+p7OHl33SxrZoUi', 1)
        self.assertEqual(1, len(result))

    def test_k8s_secret_name(self):
        # given
        test_file_path = Path(__file__).parent / "resources/k8s/secret-name.yaml"

        # when
        with open(file=str(test_file_path)) as f:
            for i, line in enumerate(f.readlines()):
                result = self.plugin.analyze_line("secret-no-false-positive2.yml", line, i)

                # then
                self.assertEqual(0, len(result))
