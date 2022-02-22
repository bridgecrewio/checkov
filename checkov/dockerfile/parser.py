from collections import OrderedDict

import re
from dockerfile_parse import DockerfileParser
from dockerfile_parse.constants import COMMENT_INSTRUCTION

# class CheckovDockerFileParser(DockerfileParser)
from checkov.common.bridgecrew.integration_features.features.policy_metadata_integration import integration as metadata_integration
from checkov.common.comment.enum import COMMENT_REGEX


def parse(filename):
    with open(filename) as dockerfile:
        dfp = DockerfileParser(fileobj=dockerfile)
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
    bc_id_mapping = metadata_integration.bc_to_ckv_id_mapping
    if COMMENT_INSTRUCTION in parse_result:
        for comment in parse_result[COMMENT_INSTRUCTION]:
            skip_search = re.search(COMMENT_REGEX, comment["value"])
            if skip_search:
                skipped_check = {
                    'id': skip_search.group(2),
                    'suppress_comment': skip_search.group(3)[1:] if skip_search.group(
                        3) else "No comment provided"
                }
                # No matter which ID was used to skip, save the pair of IDs in the appropriate fields
                if bc_id_mapping and skipped_check["id"] in bc_id_mapping:
                    skipped_check["bc_id"] = skipped_check["id"]
                    skipped_check["id"] = bc_id_mapping[skipped_check["id"]]
                elif metadata_integration.check_metadata:
                    skipped_check["bc_id"] = metadata_integration.get_bc_id(skipped_check["id"])
                skipped_checks.append(skipped_check)
    return skipped_checks

