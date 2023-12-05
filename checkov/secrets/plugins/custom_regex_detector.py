from __future__ import annotations

import logging
from typing import Set, Any, Generator, Pattern, Optional, Dict, Tuple, TYPE_CHECKING, cast

from detect_secrets.constants import VerifiedResult
from detect_secrets.core.potential_secret import PotentialSecret
from detect_secrets.plugins.base import RegexBasedDetector
from detect_secrets.util.inject import call_function_with_arguments
import re

from checkov.common.util.file_utils import read_file_safe, get_file_size_safe
from checkov.secrets.plugins.load_detectors import load_detectors

MIN_CHARACTERS = 5
MAX_CHARACTERS = 100

if TYPE_CHECKING:
    from detect_secrets.util.code_snippet import CodeSnippet


class CustomRegexDetector(RegexBasedDetector):
    secret_type = "Regex Detector"  # noqa: CCE003 # nosec
    denylist: Set[Pattern[str]] = set()  # noqa: CCE003
    MAX_FILE_SIZE: int = 4 * 1024
    MAX_LINE_LENGTH: int = 10_000

    def __init__(self) -> None:
        self.regex_to_metadata: dict[str, dict[str, Any]] = dict()
        self.denylist = set()
        self.multiline_deny_list = set()
        self.multiline_regex_to_metadata: dict[str, dict[str, Any]] = dict()
        self._analyzed_files: Set[str] = set()
        self._multiline_regex_supported_file_types: Set[str] = set()
        detectors = load_detectors()

        for detector in detectors:
            try:
                if detector.get("isMultiline"):
                    self.multiline_deny_list.add(re.compile('{}'.format(detector["Regex"])))
                    self.multiline_regex_to_metadata[detector["Regex"]] = detector
                    continue
                self.denylist.add(re.compile('{}'.format(detector["Regex"])))
                self.regex_to_metadata[detector["Regex"]] = detector
            except Exception:
                logging.error(
                    f"Failed to load detector {detector.get('Name')} with regex {detector.get('Regex')}",
                    exc_info=True,
                )

    @property
    def multiline_regex_supported_file_types(self) -> Set[str]:
        if self._multiline_regex_supported_file_types:
            return self._multiline_regex_supported_file_types
        for regex in self.multiline_regex_to_metadata.values():
            self._multiline_regex_supported_file_types.update(regex.get("supportedFiles", []))
        return self._multiline_regex_supported_file_types

    def analyze_line(
            self,
            filename: str,
            line: str,
            line_number: int = 0,
            context: Optional[CodeSnippet] = None,
            raw_context: Optional[CodeSnippet] = None,
            **kwargs: Any
    ) -> Set[PotentialSecret]:
        """This examines a line and finds all possible secret values in it"""
        output: Set[PotentialSecret] = set()

        line_length = len(line)
        if line_length > CustomRegexDetector.MAX_LINE_LENGTH:
            logging.info(f"File {filename} Line {line_number} has a length of {line_length}, which is higher than the max {CustomRegexDetector.MAX_LINE_LENGTH}")
            return output

        self._find_potential_secret(
            filename=filename,
            string_to_analyze=line,
            output=output,
            line_number=line_number,
            context=raw_context,
            is_multiline=False,
            **kwargs
        )

        if filename not in self._analyzed_files:
            self._analyzed_files.add(filename)
            # We only want to read file if: there is regex supporting it & file size is not over MAX_FILE_SIZE
            if not self.multiline_regex_to_metadata.values() or \
                    not self.multiline_regex_supported_file_types or \
                    not any([filename.endswith(str(file_type)) for file_type in self.multiline_regex_supported_file_types]) or \
                    not 0 < get_file_size_safe(filename) < CustomRegexDetector.MAX_FILE_SIZE:
                return output
            file_content = read_file_safe(filename)
            if not file_content:
                return output

            self._find_potential_secret(
                filename=filename,
                string_to_analyze=file_content,
                output=output,
                line_number=1,
                context=raw_context,
                is_multiline=True,
                **kwargs
            )

        return output

    def _find_potential_secret(
            self,
            filename: str,
            string_to_analyze: str,
            output: Set[PotentialSecret],
            line_number: int = 0,
            context: Optional[CodeSnippet] = None,
            is_multiline: bool = False,
            is_added: bool = False,
            is_removed: bool = False,
            **kwargs: Any
    ) -> None:
        current_denylist: Set[Pattern[str]] = set()
        if is_multiline:
            # We want the multiline regex to execute only if current file is supported by them
            for regex in self.multiline_deny_list:
                regex_supported_files = self.multiline_regex_to_metadata.get(regex.pattern, {}).get("supportedFiles", [])
                if regex_supported_files and any([filename.endswith(regex_supported_file) for regex_supported_file in regex_supported_files]):
                    current_denylist.add(regex)
        else:
            current_denylist = self.denylist

        current_regex_to_metadata: dict[str, dict[str, Any]] = self.multiline_regex_to_metadata if is_multiline else self.regex_to_metadata
        kwargs["regex_denylist"] = current_denylist
        for match, regex in self.analyze_string(string_to_analyze, **kwargs):
            try:
                verified_result = call_function_with_arguments(self.verify, secret=match, context=context)
                is_verified = True if verified_result == VerifiedResult.VERIFIED_TRUE else False
            except Exception:
                is_verified = False
            regex_data = current_regex_to_metadata[regex.pattern]
            # Wrap multiline match with fstring + ''
            match = f"'{match}'" if is_multiline else match
            ps = PotentialSecret(
                type=regex_data["Name"],
                filename=filename,
                secret=match,
                line_number=line_number,
                is_verified=is_verified,
                is_added=is_added,
                is_removed=is_removed,
                is_multiline=is_multiline,
            )
            ps.check_id = current_regex_to_metadata[regex.pattern]["Check_ID"]
            if is_multiline:
                output.add(ps)
            elif len(cast(str, ps.secret_value)) in range(MIN_CHARACTERS, MAX_CHARACTERS) or not regex_data['isCustom']:
                output.add(ps)
            else:
                logging.info(
                    f'Finding for check {ps.check_id} are not 5-100 characters in length, was ignored')

    def analyze_string(self, string: str, **kwargs: Optional[Dict[str, Any]]) -> Generator[Tuple[str, Pattern[str]], None, None]:  # type:ignore[override]
        regex_denylist: Set[Pattern[str]] = kwargs.get("regex_denylist", self.denylist)  # type: ignore[assignment]
        for regex in regex_denylist:
            for match in regex.findall(string):
                if isinstance(match, tuple):
                    for submatch in filter(bool, match):
                        # It might make sense to paste break after yielding
                        yield submatch, regex
                else:
                    yield match, regex
