from __future__ import annotations

import re
from typing import TYPE_CHECKING

from checkov.common.parsers.multiline_parser import BaseMultiLineParser

if TYPE_CHECKING:
	from detect_secrets.util.code_snippet import CodeSnippet


INDENTATION_PATTERN = re.compile(r'(^\s*(?:-?\s+)?)')
COMMENT_PREFIX = re.compile(r'^[\s]*(#|\/\/)')


class YamlMultilineParser(BaseMultiLineParser):

	def __init__(self):
		super().__init__()

	def get_lines_from_same_object(
			self,
			search_range: range,
			context: CodeSnippet | None,
			raw_context: CodeSnippet | None
	) -> set[str]:
		possible_keywords: set[str] = set()
		if not context or not raw_context:
			return possible_keywords
		for j in search_range:
			line = context.lines[j]
			if self.lines_in_same_object(raw_context=raw_context, idx=j) and not self.is_line_comment(line):
				possible_keywords.add(raw_context.lines[j])
				if self.is_object_start(raw_context=raw_context, idx=j):
					return possible_keywords
		return possible_keywords

	def lines_in_same_object(
			self,
			raw_context: CodeSnippet | None,
			idx: int
	) -> bool:
		if not raw_context:
			return False  # could not know
		return 0 <= idx < len(raw_context.lines) and 0 <= idx + 1 < len(raw_context.lines) \
			and self.lines_same_indentation(raw_context.lines[idx], raw_context.lines[idx + 1])

	@staticmethod
	def is_object_start(
			raw_context: CodeSnippet | None,
			idx: int
	) -> bool:
		if not raw_context:
			return False  # could not know
		match = re.match(INDENTATION_PATTERN, raw_context.lines[idx])
		if match:
			return '-' in match.groups()[0]
		return False

	@staticmethod
	def is_line_comment(line: str) -> bool:
		if re.match(COMMENT_PREFIX, line):
			return True
		return False

	@staticmethod
	def lines_same_indentation(line1: str, line2: str) -> bool:
		match1 = re.match(INDENTATION_PATTERN, line1)
		match2 = re.match(INDENTATION_PATTERN, line2)
		if not match1 and not match2:
			return True
		if not match1 or not match2:
			return False
		indent1 = len(match1.groups()[0])
		indent2 = len(match2.groups()[0])
		if indent1 == indent2:
			return True
		return False


yaml_multiline_parser = YamlMultilineParser()
