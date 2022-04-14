from __future__ import annotations

from collections import OrderedDict
from pathlib import Path

from dockerfile_parse import DockerfileParser
from dockerfile_parse.constants import COMMENT_INSTRUCTION

from checkov.common.typing import _SkippedCheck
from checkov.common.util.suppression import collect_suppressions_for_context


def parse(filename: str | Path) -> tuple[dict[str, list[dict[str, int | str]]], list[str]]:
    with open(filename) as dockerfile:
        dfp = DockerfileParser(fileobj=dockerfile)
        return dfp_group_by_instructions(dfp)


def dfp_group_by_instructions(dfp: DockerfileParser) -> tuple[dict[str, list[dict[str, int | str]]], list[str]]:
    result: dict[str, list[dict[str, int | str]]] = OrderedDict()
    for instruction in dfp.structure:
        instruction_literal = instruction["instruction"]
        if instruction_literal not in result:
            result[instruction_literal] = []
        result[instruction_literal].append(instruction)
    return result, dfp.lines


def collect_skipped_checks(parse_result: dict[str, list[dict[str, int | str]]]) -> list[_SkippedCheck]:
    skipped_checks = []

    if COMMENT_INSTRUCTION in parse_result:
        # line number doesn't matter
        comment_lines = [(0, comment["value"]) for comment in parse_result[COMMENT_INSTRUCTION]]
        skipped_checks = collect_suppressions_for_context(code_lines=comment_lines)

    return skipped_checks
