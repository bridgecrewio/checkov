import logging
import re
from abc import ABC, abstractmethod
from itertools import islice
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

import dpath.util

from checkov.common.bridgecrew.platform_integration import bc_integration
from checkov.common.comment.enum import COMMENT_REGEX
from checkov.common.models.enums import ContextCategories
from checkov.terraform.context_parsers.registry import parser_registry

OPEN_CURLY = "{"
CLOSE_CURLY = "}"


class BaseContextParser(ABC):
    definition_type = ""
    tf_file = ""
    tf_file_path: Optional[Path] = None
    file_lines: List[Tuple[int, str]] = []
    filtered_lines: List[Tuple[int, str]] = []
    context: Dict[str, Any] = {}

    def __init__(self, definition_type: str) -> None:
        # bc_integration.setup_http_manager()
        self.logger = logging.getLogger("{}".format(self.__module__))
        if definition_type.upper() not in ContextCategories.__members__:
            self.logger.error("Terraform context parser type not supported yet")
            raise Exception()
        self.definition_type = definition_type
        parser_registry.register(self)

    @abstractmethod
    def get_entity_context_path(self, entity_block: Dict[str, Dict[str, Any]]) -> List[str]:
        """
        returns the entity's path in the context parser
        :param entity_block: entity definition block
        :return: list of nested entity's keys in the context parser
        """
        raise NotImplementedError

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
        return self.filtered_lines

    def _read_file_lines(self) -> List[Tuple[int, str]]:
        with (open(self.tf_file, "r")) as file:
            file.seek(0)
            file_lines = [(ind + 1, line) for (ind, line) in list(enumerate(file.readlines()))]
            return file_lines

    @staticmethod
    def is_optional_comment_line(line: str) -> bool:
        line_without_whitespace = "".join(line.split())
        return 'checkov:skip=' in line_without_whitespace or 'bridgecrew:skip=' in line_without_whitespace

    def _collect_skip_comments(self, definition_blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Collects checkov skip comments to all definition blocks
        :param definition_blocks: parsed definition blocks
        :return: context enriched with with skipped checks per skipped entity
        """
        bc_id_mapping = bc_integration.get_id_mapping()
        parsed_file_lines = self.filtered_lines
        optional_comment_lines = [
            line for line in parsed_file_lines
            if self.is_optional_comment_line(line[1])
        ]
        comments = [
            (
                line_num,
                {
                    "id": match.group(2),
                    "suppress_comment": match.group(3)[1:] if match.group(3) else "No comment provided",
                },
            )
            for (line_num, x) in optional_comment_lines
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
                if entity_context["start_line"] < skip_check_line_num < entity_context["end_line"]:
                    if bc_id_mapping and skip_check["id"] in bc_id_mapping:
                        skip_check["id"] = bc_id_mapping[skip_check["id"]]
                    skipped_checks.append(skip_check)
            dpath.new(self.context, entity_context_path + ["skipped_checks"], skipped_checks)
        return self.context

    def _compute_definition_end_line(self, start_line_num: int) -> int:
        """ Given the code block's start line, compute the block's end line
        :param start_line_num: code block's first line number (the signature line)
        :return: the code block's last line number
        """
        parsed_file_lines = self.filtered_lines
        start_line_idx = [line_num for (line_num, _) in parsed_file_lines].index(start_line_num)
        i = 1
        end_line_num = 0
        for (line_num, line) in islice(parsed_file_lines, start_line_idx + 1, None):
            if OPEN_CURLY in line:
                i = i + 1
            if CLOSE_CURLY in line:
                i = i - 1
                if i == 0:
                    end_line_num = line_num
                    break
        return end_line_num

    def run(
            self, tf_file: str, definition_blocks: List[Dict[str, Any]], collect_skip_comments: bool = True
    ) -> Dict[str, Any]:
        # TF files for loaded modules have this formation:  <file>[<referrer>#<index>]
        # Chop off everything after the file name for our purposes here
        if tf_file.endswith("]") and "[" in tf_file:
            self.tf_file = tf_file[: tf_file.index("[")]
            self.tf_file_path = Path(tf_file[: tf_file.index("[")])
        else:
            self.tf_file = tf_file
            self.tf_file_path = Path(tf_file)
        self.context = {}
        self.file_lines = self._read_file_lines()
        self.context = self.enrich_definition_block(definition_blocks)
        if collect_skip_comments:
            self.context = self._collect_skip_comments(definition_blocks)
        return self.context

    def get_block_type(self) -> str:
        return self.definition_type

    @staticmethod
    def _clean_line(line: str):
        res = line.replace('"', ' ')
        if '"{' in res:
            res = res.split('{')[0]
        return res

    def enrich_definition_block(self, definition_blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Enrich the context of a Terraform block
        :param definition_blocks: Terraform block, key-value dictionary
        :return: Enriched block context
        """
        parsed_file_lines = self._filter_file_lines()
        potential_block_start_lines = [
            (ind, line) for (ind, line) in parsed_file_lines if line.startswith(self.get_block_type())
        ]
        for i, entity_block in enumerate(definition_blocks):
            entity_context_path = self.get_entity_context_path(entity_block)
            for line_num, line in potential_block_start_lines:
                line_str = self._clean_line(line)
                line_tokens = line_str.split()
                if self._is_block_signature(line_num, line_tokens, entity_context_path):
                    logging.debug(f'created context for {" ".join(entity_context_path)}')
                    start_line = line_num
                    end_line = self._compute_definition_end_line(line_num)
                    dpath.new(self.context, entity_context_path + ["start_line"], start_line)
                    dpath.new(self.context, entity_context_path + ["end_line"], end_line)
                    dpath.new(
                        self.context, entity_context_path + ["code_lines"], self.file_lines[start_line - 1: end_line]
                    )
                    potential_block_start_lines.remove((line_num, line))
                    break
        return self.context
