from __future__ import annotations

import logging
import re
from abc import ABC, abstractmethod
from collections import defaultdict
from itertools import islice
from pathlib import Path
from typing import List, Dict, Any, Tuple

import dpath.util

from checkov.common.bridgecrew.integration_features.features.policy_metadata_integration import integration as metadata_integration
from checkov.common.comment.enum import COMMENT_REGEX
from checkov.common.models.enums import ContextCategories
from checkov.common.util.parser_utils import get_abs_path
from checkov.terraform.context_parsers.registry import parser_registry

OPEN_CURLY = "{"
CLOSE_CURLY = "}"


class BaseContextParser(ABC):
    def __init__(self, definition_type: str) -> None:
        # bc_integration.setup_http_manager()
        self.logger = logging.getLogger("{}".format(self.__module__))
        if definition_type.upper() not in ContextCategories.__members__:
            self.logger.error("Terraform context parser type not supported yet")
            raise Exception()
        self.definition_type = definition_type
        self.tf_file = ""
        self.tf_file_path: Path | None = None
        self.file_lines: list[tuple[int, str]] = []
        self.filtered_lines: list[tuple[int, str]] = []
        self.filtered_line_numbers: list[int] = []
        self.context: dict[str, Any] = defaultdict(dict)

        parser_registry.register(self)

    @abstractmethod
    def get_entity_context_path(self, entity_block: Dict[str, Dict[str, Any]]) -> List[str]:
        """
        returns the entity's path in the context parser
        :param entity_block: entity definition block
        :return: list of nested entity's keys in the context parser
        """
        raise NotImplementedError

    def get_entity_definition_path(self, entity_block: Dict[str, Dict[str, Any]]) -> List[str]:
        """
        returns the entity's path in the entity definition block
        :param entity_block: entity definition block
        :return: list of nested entity's keys in the entity definition block
        """
        return self.get_entity_context_path(entity_block)

    def _is_block_signature(self, line_num: int, line_tokens: List[str], entity_context_path: List[str]) -> bool:
        """
        Determine if the given tokenized line token is the entity signature line
        :param line_num: The line number in the file
        :param line_tokens: list of line tokens
        :param entity_context_path: the entity's path in the context parser
        :return: True/False
        """
        block_type = self.get_block_type()
        return all(x in line_tokens for x in [block_type] + entity_context_path)

    @staticmethod
    def _trim_whitespaces_linebreaks(text: str) -> str:
        return text.strip()

    def _filter_file_lines(self) -> List[Tuple[int, str]]:
        parsed_file_lines = [(ind, self._trim_whitespaces_linebreaks(line)) for (ind, line) in self.file_lines]
        self.filtered_lines = [(ind, line) for (ind, line) in parsed_file_lines if line]
        self.filtered_line_numbers = [ind for ind, _ in self.filtered_lines]
        return self.filtered_lines

    def _read_file_lines(self) -> List[Tuple[int, str]]:
        with open(self.tf_file, "r") as file:
            file.seek(0)
            file_lines = [(ind + 1, line) for ind, line in enumerate(file.readlines())]
            return file_lines

    @staticmethod
    def is_optional_comment_line(line: str) -> bool:
        line_without_whitespace = line.replace(" ", "")
        return "checkov:skip=" in line_without_whitespace or "bridgecrew:skip=" in line_without_whitespace

    def _collect_skip_comments(self, definition_blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Collects checkov skip comments to all definition blocks
        :param definition_blocks: parsed definition blocks
        :return: context enriched with with skipped checks per skipped entity
        """
        bc_id_mapping = metadata_integration.bc_to_ckv_id_mapping
        comments = [
            (
                line_num,
                {
                    "id": match.group(2),
                    "suppress_comment": match.group(3)[1:] if match.group(3) else "No comment provided",
                },
            )
            for (line_num, x) in self.file_lines
            if self.is_optional_comment_line(x)
            for match in [re.search(COMMENT_REGEX, x)]
            if match
        ]
        for entity_block in definition_blocks:
            skipped_checks = []
            entity_context_path = self.get_entity_context_path(entity_block)
            entity_context = self.context
            found = True
            for k in entity_context_path:
                if k in entity_context:
                    entity_context = entity_context[k]
                else:
                    logging.warning(f'Failed to find context for {".".join(entity_context_path)}')
                    found = False
                    break
            if not found:
                continue
            for (skip_check_line_num, skip_check) in comments:
                if "start_line" in entity_context and "end_line" in entity_context \
                        and entity_context["start_line"] < skip_check_line_num < entity_context["end_line"]:
                    # No matter which ID was used to skip, save the pair of IDs in the appropriate fields
                    if bc_id_mapping and skip_check["id"] in bc_id_mapping:
                        skip_check["bc_id"] = skip_check["id"]
                        skip_check["id"] = bc_id_mapping[skip_check["id"]]
                    elif metadata_integration.check_metadata:
                        skip_check["bc_id"] = metadata_integration.get_bc_id(skip_check["id"])
                    skipped_checks.append(skip_check)
            dpath.new(self.context, entity_context_path + ["skipped_checks"], skipped_checks)
        return self.context

    def _compute_definition_end_line(self, start_line_num: int) -> int:
        """Given the code block's start line, compute the block's end line
        :param start_line_num: code block's first line number (the signature line)
        :return: the code block's last line number
        """
        parsed_file_lines = self.filtered_lines
        start_line_idx = self.filtered_line_numbers.index(start_line_num)
        i = 0
        end_line_num = 0
        for (line_num, line) in islice(parsed_file_lines, start_line_idx, None):
            if OPEN_CURLY in line:
                i += line.count(OPEN_CURLY)
            if CLOSE_CURLY in line:
                i -= line.count(CLOSE_CURLY)
                if i == 0:
                    end_line_num = line_num
                    break
        return end_line_num

    def run(
            self, tf_file: str, definition_blocks: List[Dict[str, Any]], collect_skip_comments: bool = True
    ) -> Dict[str, Any]:
        # TF files for loaded modules have this formation:  <file>[<referrer>#<index>]
        # Chop off everything after the file name for our purposes here
        self.tf_file = get_abs_path(tf_file)
        self.tf_file_path = Path(self.tf_file)
        self.context = defaultdict(dict)
        self.file_lines = self._read_file_lines()
        self.context = self.enrich_definition_block(definition_blocks)
        if collect_skip_comments:
            self.context = self._collect_skip_comments(definition_blocks)
        return self.context

    def get_block_type(self) -> str:
        return self.definition_type

    @staticmethod
    def _clean_line(line: str) -> str:
        res = line.replace('"', " ")
        if '"{' in res:
            res = res.split("{")[0]
        return res

    @abstractmethod
    def enrich_definition_block(self, definition_blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Enrich the context of a Terraform block
        :param definition_blocks: Terraform block, key-value dictionary
        :return: Enriched block context
        """
        pass
