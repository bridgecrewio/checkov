import unittest
from pathlib import Path

from checkov.secrets.parsers.yaml.multiline_parser import yml_multiline_parser


class TestMultilineParserYml(unittest.TestCase):
	def setUp(self) -> None:
		self.yml_parser = yml_multiline_parser

	def test_are_lines_same_indentation_yml(self):
		test_file_path = Path(__file__).parent / "resources/cfn/secret.yml"

		result = {0: True, 1: False, 2: False, 3: False, 4: False, 5: True, 6: False, 7: True,
				  8: True, 9: True, 10: True, 11: False, 12: False, 13: False, 14: False, 15: False,
				  16: True, 17: False, 18: False, 19: True, 20: True, 21: True}
		with open(file=test_file_path) as f:
			lines = f.readlines()
			# assert len(result) == len(lines)-1
			for i in range(len(lines) - 1):
				result[i] = self.yml_parser.lines_same_indentation(lines[i], lines[i + 1])

		assert result

	def test_line_is_comment_yml(self):
		examples = [
			(True, "# comment"),
			(True, "     # also comment"),
			(True, "// nice comment here"),
			(True, "//and nice comment here2"),
			(True, "      // commenting with checkov and having fun"),
			(False, "var: a  //this is not a comment"),
			(False, "var: not a comment # comment"),
			(False, "  - var: a"),
			(False, "var: "),
		]

		for ans, line in examples:
			assert ans == self.yml_parser.is_line_comment(line)