from __future__ import annotations

from collections import OrderedDict
from pathlib import Path
from typing import TYPE_CHECKING
import io
import re

from dockerfile_parse import DockerfileParser
from dockerfile_parse.constants import COMMENT_INSTRUCTION

from checkov.common.typing import _SkippedCheck
from checkov.common.util.suppression import collect_suppressions_for_context

if TYPE_CHECKING:
    from dockerfile_parse.parser import _Instruction  # only in extra_stubs


def parse(filename: str | Path) -> tuple[dict[str, list[_Instruction]], list[str]]:
    with open(filename) as dockerfile:
        content = dockerfile.read()
        converted_content = convert_multiline_commands(content)
        dfp = DockerfileParser(fileobj=io.StringIO(converted_content))
        return dfp_group_by_instructions(dfp)


def dfp_group_by_instructions(dfp: DockerfileParser) -> tuple[dict[str, list[_Instruction]], list[str]]:
    result: dict[str, list[_Instruction]] = OrderedDict()
    for instruction in dfp.structure:
        instruction_literal = instruction["instruction"]
        if instruction_literal not in result:
            result[instruction_literal] = []
        result[instruction_literal].append(instruction)
    return result, dfp.lines


def collect_skipped_checks(parse_result: dict[str, list[_Instruction]]) -> list[_SkippedCheck]:
    skipped_checks = []

    if COMMENT_INSTRUCTION in parse_result:
        # line number doesn't matter
        comment_lines = [(0, comment["value"]) for comment in parse_result[COMMENT_INSTRUCTION]]
        skipped_checks = collect_suppressions_for_context(code_lines=comment_lines)

    return skipped_checks


_HEREDOC_START_PATTERN = re.compile(r"^RUN\s+<<-?\s*[\"']?(\w+)[\"']?")
_HEREDOC_DELIMITER_PATTERN = re.compile(r"<<-?\s*[\"']?(\w+)[\"']?")


def convert_multiline_commands(dockerfile_content: str) -> str:
    """Fold heredoc bodies (``RUN <<DELIM`` ... ``DELIM``) into a single RUN line.

    ``dockerfile_parse`` does not understand heredocs, so without this folding
    the heredoc body lines are parsed as Docker instructions and surface as
    unsupported-instruction warnings.  Any delimiter word is supported
    (``<<EOF``, ``<<EOT``, ``<<-EOT``, quoted delimiters, ...), including
    multiple heredocs on a single RUN line.
    """
    lines = dockerfile_content.splitlines()
    converted_lines: list[str] = []
    heredoc_delimiters: list[str] = []
    heredoc_body: list[str] = []

    for line in lines:
        stripped_line = line.strip()

        if heredoc_delimiters:
            if stripped_line == heredoc_delimiters[0]:
                heredoc_delimiters.pop(0)
                if not heredoc_delimiters:
                    converted_lines.append(f"RUN {' && '.join(heredoc_body)}")
                    heredoc_body = []
            else:
                heredoc_body.append(stripped_line)
            continue

        if _HEREDOC_START_PATTERN.match(stripped_line):
            heredoc_delimiters = _HEREDOC_DELIMITER_PATTERN.findall(stripped_line)
            continue

        converted_lines.append(line)

    return '\n'.join(converted_lines)


