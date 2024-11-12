from __future__ import annotations

from collections import OrderedDict
from pathlib import Path
from typing import TYPE_CHECKING
import io

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


def convert_multiline_commands(dockerfile_content: str) -> str:
    lines = dockerfile_content.splitlines()
    converted_lines = []
    in_multiline = False
    multiline_command: list[str] = []

    for line in lines:
        if line.strip().startswith('RUN <<EOF'):
            in_multiline = True
            continue
        elif in_multiline and line.strip() == 'EOF':
            in_multiline = False
            converted_lines.append(f"RUN {' && '.join(multiline_command)}")
            multiline_command = []
        elif in_multiline:
            multiline_command.append(line.strip())
        else:
            converted_lines.append(line)

    return '\n'.join(converted_lines)
