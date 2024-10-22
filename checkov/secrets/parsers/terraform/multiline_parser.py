from __future__ import annotations

import re
from typing import TYPE_CHECKING

from checkov.secrets.parsers.multiline_parser import BaseMultiLineParser

if TYPE_CHECKING:
    from detect_secrets.util.code_snippet import CodeSnippet

START_OBJ = re.compile(r"^\s*\w*\s*=?\s*{\s*$")
END_OBJ = re.compile(r"^\s*}\s*$")
COMMENT_PREFIX = re.compile(r"^[\s]*(#|//)")


class TerraformMultiLineParser(BaseMultiLineParser):
    def consecutive_lines_in_same_object(
        self,
        raw_context: CodeSnippet | None,
        other_line_idx: int,
    ) -> bool:
        return bool(raw_context and 0 <= other_line_idx < len(raw_context.lines))

    @staticmethod
    def is_object_start(line: str) -> bool:
        return bool(re.match(START_OBJ, line))

    @staticmethod
    def is_object_end(line: str) -> bool:
        return bool(re.match(END_OBJ, line))

    @staticmethod
    def is_line_comment(line: str) -> bool:
        return bool(re.match(COMMENT_PREFIX, line))


terraform_multiline_parser = TerraformMultiLineParser()
