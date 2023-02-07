from __future__ import annotations

import logging
from typing import Set, Any, Generator, Pattern, Optional, Dict, Tuple, TYPE_CHECKING, cast


from detect_secrets.constants import VerifiedResult
from detect_secrets.core.potential_secret import PotentialSecret
from detect_secrets.plugins.base import RegexBasedDetector
from detect_secrets.util.inject import call_function_with_arguments
import re

from checkov.secrets.plugins.load_detectors import load_detectors

MIN_CHARACTERS = 5
MAX_CHARACTERS = 100

if TYPE_CHECKING:
    from detect_secrets.util.code_snippet import CodeSnippet


class CustomRegexDetector(RegexBasedDetector):
    secret_type = "Regex Detector"  # noqa: CCE003 # nosec
    denylist: Set[Pattern[str]] = set()  # noqa: CCE003

    def __init__(self) -> None:
        self.regex_to_metadata: dict[str, dict[str, Any]] = dict()
        self.denylist = set()
        self.multiline_deny_list = set()
        self.multiline_regex_to_metadata: dict[str, dict[str, Any]] = dict()
        self._analyzed_files: Set[str] = set()
        detectors = load_detectors()

        for detector in detectors:
            if detector.get("isMultiline"):
                self.multiline_deny_list.add(re.compile('{}'.format(detector["Regex"])))
                self.multiline_regex_to_metadata[detector["Regex"]] = detector
                continue
            self.denylist.add(re.compile('{}'.format(detector["Regex"])))
            self.regex_to_metadata[detector["Regex"]] = detector

    def analyze_line(
            self,
            filename: str,
            line: str,
            line_number: int = 0,
            context: Optional[CodeSnippet] = None,
            raw_context: Optional[CodeSnippet] = None,
            is_added: bool = False,
            is_removed: bool = False,
            **kwargs: Any
    ) -> Set[PotentialSecret]:
        """This examines a line and finds all possible secret values in it"""
        output: Set[PotentialSecret] = set()

        self._find_potential_secret(
            filename=filename,
            string_to_analyze=line,
            output=output,
            line_number=line_number,
            context=raw_context,
            is_multiline=False,
            **kwargs
        )

        # ToDo: Comment out once fix performence #  type: ignore
        # if filename not in self._analyzed_files:
        #     self._analyzed_files.add(filename)
        #     file_content = None
        #     try:
        #         with open(filename, 'r') as f:
        #             file_content = f.read()
        #     except Exception:
        #         logging.warning(
        #             "Could not open file in order to detect secrets}",
        #             extra={"file_path": filename}
        #         )
        #     if not file_content:
        #         return output
        # this should be indented:
        # self._find_potential_secret(
        #     filename=filename,
        #     string_to_analyze=file_content,
        #     output=output,
        #     line_number=0,
        #     context=raw_context,
        #     is_multiline=True,
        #     **kwargs
        # )

        return output

    def _find_potential_secret(
            self,
            filename: str,
            string_to_analyze: str,
            output: Set[PotentialSecret],
            line_number: int = 0,
            context: Optional[CodeSnippet] = None,
            is_multiline: bool = False,
            **kwargs: Any
    ) -> None:
        current_denylist: Set[Pattern[str]] = self.multiline_deny_list if is_multiline else self.denylist
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
                is_verified=is_verified
            )
            ps.check_id = current_regex_to_metadata[regex.pattern]["Check_ID"]  # type:ignore[attr-defined]
            if is_multiline:
                output.add(ps)
            elif len(cast(str, ps.secret_value)) in range(MIN_CHARACTERS, MAX_CHARACTERS) or not regex_data['isCustom']:
                output.add(ps)
            else:
                logging.info(
                    f'Finding for check {ps.check_id} are not 5-100 characters in length, was ignored')  # type: ignore

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
