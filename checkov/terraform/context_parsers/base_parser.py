import logging
import re
from abc import ABC, abstractmethod
from checkov.terraform.context_parsers.registry import parser_registry
from checkov.terraform.models.enums import ContextCategories
from itertools import islice

OPEN_CURLY = '{'
CLOSE_CURLY = '}'
COMMENT_REGEX = re.compile('(checkov:skip=) *([A-Z_\d]+)(:[^\n]+)?')


class BaseContextParser(ABC):
    definition_type = ""
    tf_file = ""
    file_lines = []
    context = {}

    def __init__(self, definition_type):
        self.logger = logging.getLogger("{}".format(self.__module__))
        if definition_type not in ContextCategories.__members__:
            self.logger.error("Terraform context parser type not supported yet")
            raise Exception()
        self.definition_type = definition_type
        parser_registry.register(self)

    @staticmethod
    def _trim_whitespaces_linebreaks(text):
        return re.sub('\s+', ' ', text).strip()

    def _filter_file_lines(self):
        parsed_file_lines = [(ind, self._trim_whitespaces_linebreaks(line)) for (ind, line) in self.file_lines]
        return [(ind, line) for (ind, line) in parsed_file_lines if line]

    def _read_file_lines(self, tf_file):
        self.tf_file = tf_file
        with(open(tf_file, 'r')) as file:
            file.seek(0)
            file_lines = [(ind + 1, line) for (ind, line) in
                          list(enumerate(file.readlines()))]
            return file_lines

    def _collect_skip_comments(self):
        parsed_file_lines = self._filter_file_lines()
        comments = [(line_num, {"id": re.search(COMMENT_REGEX, x).group(2),
                                "suppress_comment": re.search(COMMENT_REGEX, x).group(3)[1:] if re.search(COMMENT_REGEX,
                                                                                                          x).group(3)
                                else "No comment provided"}) for (line_num, x) in
                    parsed_file_lines if re.search(COMMENT_REGEX, x)]
        for (skip_check_line_num, skip_check) in comments:
            for (block_type, block_def) in self.context.items():
                for (block_name, block_context) in block_def.items():
                    if block_context['start_line'] < skip_check_line_num < block_context['end_line']:
                        self.context[block_type][block_name].setdefault('skipped_checks', []).append(skip_check)
        return self.context

    def _compute_definition_end_line(self, start_line_num):
        parsed_file_lines = self._filter_file_lines()
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

    def run(self, tf_file, block):
        self.file_lines = self._read_file_lines(tf_file)
        self.context = self.enrich_definition_block(block)
        self.context = self._collect_skip_comments()
        return self.context

    @abstractmethod
    def enrich_definition_block(self, block):
        raise NotImplementedError()
