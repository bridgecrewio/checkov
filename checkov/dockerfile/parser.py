from collections import OrderedDict

import re
from dockerfile_parse import DockerfileParser
from dockerfile_parse.constants import COMMENT_INSTRUCTION

# class CheckovDockerFileParser(DockerfileParser)
from checkov.common.comment.enum import COMMENT_REGEX


def parse(filename):
    dfp = DockerfileParser(path=filename)
    return dfp_group_by_instructions(dfp)


def dfp_group_by_instructions(dfp):
    result = OrderedDict()
    for instruction in dfp.structure:
        instruction_literal = instruction["instruction"]
        if instruction_literal not in result:
            result[instruction_literal] = []
        result[instruction_literal].append(instruction)
    return result, dfp.lines


def collect_skipped_checks(parse_result):
    skipped_checks = []
    if COMMENT_INSTRUCTION in parse_result:
        for comment in parse_result[COMMENT_INSTRUCTION]:
            skip_search = re.search(COMMENT_REGEX, comment["value"])
            if skip_search:
                skipped_checks.append(
                    {
                        'id': skip_search.group(2),
                        'suppress_comment': skip_search.group(3)[1:] if skip_search.group(
                            3) else "No comment provided"
                    }
                )
    return skipped_checks

