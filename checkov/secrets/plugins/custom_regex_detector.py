from __future__ import annotations

import logging
from typing import Set, Any, Generator, Pattern, Optional, Dict, Tuple, List, TYPE_CHECKING, cast

from checkov.common.bridgecrew.integration_features.features.policy_metadata_integration import \
    integration as metadata_integration
import yaml
from detect_secrets.constants import VerifiedResult
from detect_secrets.core.potential_secret import PotentialSecret
from detect_secrets.plugins.base import RegexBasedDetector
from detect_secrets.util.inject import call_function_with_arguments
import re

from checkov.common.bridgecrew.platform_integration import bc_integration

MIN_CHARACTERS = 5
MAX_CHARACTERS = 100

if TYPE_CHECKING:
    from detect_secrets.util.code_snippet import CodeSnippet


def load_detectors() -> list[dict[str, Any]]:
    detectors: List[dict[str, Any]] = []
    try:
        customer_run_config_response = bc_integration.customer_run_config_response
        policies_list: List[dict[str, Any]] = []
        if customer_run_config_response:
            policies_list = customer_run_config_response.get('secretsPolicies', [])
    except Exception as e:
        logging.error(f"Failed to get detectors from customer_run_config_response, error: {e}")
        return []

    if policies_list:
        detectors = modify_secrets_policy_to_detectors(policies_list)
    if detectors:
        logging.info(f"Successfully loaded {len(detectors)} detectors from bc_integration")
    return detectors


def modify_secrets_policy_to_detectors(policies_list: List[dict[str, Any]]) -> List[dict[str, Any]]:
    secrets_list = transforms_policies_to_detectors_list(policies_list)
    logging.info(f"(modify_secrets_policy_to_detectors) secrets_list = {secrets_list}")
    return secrets_list


def add_to_custom_detectors(custom_detectors: List[Dict[str, Any]], name: str, check_id: str, regex: str, is_custom: str) -> None:
    custom_detectors.append({'Name': name,
                             'Check_ID': check_id,
                             'Regex': regex,
                             'isCustom': is_custom})
    if is_custom:
        metadata_integration.check_metadata[check_id] = {'id': check_id}


def add_detectors_from_condition_query(custom_detectors: List[Dict[str, Any]], condition_query: Dict[str, Any], secret_policy: Dict[str, Any], check_id: str) -> bool:
    parsed = False
    cond_type = condition_query['cond_type']
    if cond_type == 'secrets':
        value = condition_query['value']
        if type(value) is str:
            value = [value]
        for regex in value:
            parsed = True
            add_to_custom_detectors(custom_detectors, secret_policy['title'], check_id, regex, secret_policy['isCustom'])
            logging.info(f"Regex : {secret_policy['title']} added to custom_detectors")
    return parsed


def add_detectors_from_code(custom_detectors: List[Dict[str, Any]], code: str, secret_policy: Dict[str, Any], check_id: str) -> bool:
    parsed = False
    code_dict = yaml.safe_load(code)
    if 'definition' in code_dict:
        if 'value' in code_dict['definition']:
            parsed = True
            if type(code_dict['definition']['value']) is str:
                code_dict['definition']['value'] = [code_dict['definition']['value']]
            for regex in code_dict['definition']['value']:
                add_to_custom_detectors(custom_detectors, secret_policy['title'], check_id, regex,
                                        secret_policy['isCustom'])
                logging.info(f"Regex : {secret_policy['title']} added to custom_detectors")
    return parsed


def transforms_policies_to_detectors_list(custom_secrets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    custom_detectors: List[Dict[str, Any]] = []
    condition_query = None
    for secret_policy in custom_secrets:
        parsed = False
        check_id = secret_policy['checkovCheckId'] if secret_policy['checkovCheckId'] else \
            secret_policy['incidentId']
        code = secret_policy['code']
        if 'conditionQuery' in secret_policy:
            condition_query = secret_policy['conditionQuery']
        if condition_query:
            parsed = add_detectors_from_condition_query(custom_detectors, condition_query, secret_policy, check_id)
        elif code:
            parsed = add_detectors_from_code(custom_detectors, code, secret_policy, check_id)
        if not parsed:
            logging.info(f"policy : {secret_policy} could not be parsed")
    return custom_detectors


class CustomRegexDetector(RegexBasedDetector):
    secret_type = "Regex Detector"  # noqa: CCE003 # nosec
    denylist: Set[Pattern[str]] = set()  # noqa: CCE003

    def __init__(self) -> None:
        self.regex_to_metadata: dict[str, dict[str, Any]] = dict()
        self.denylist = set()
        detectors = load_detectors()

        for detector in detectors:
            self.denylist.add(re.compile('{}'.format(detector["Regex"])))
            self.regex_to_metadata[detector["Regex"]] = detector

    def analyze_line(
            self,
            filename: str,
            line: str,
            line_number: int = 0,
            context: Optional[CodeSnippet] = None,
            raw_context: Optional[CodeSnippet] = None,
            **kwargs: Any
    ) -> Set[PotentialSecret]:
        """This examines a line and finds all possible secret values in it."""
        output: Set[PotentialSecret] = set()
        for match, regex in self.analyze_string(line, **kwargs):
            try:
                verified_result = call_function_with_arguments(self.verify, secret=match, context=context)
                is_verified = True if verified_result == VerifiedResult.VERIFIED_TRUE else False
            except Exception:
                is_verified = False
            regex_data = self.regex_to_metadata[regex.pattern]
            ps = PotentialSecret(type=regex_data["Name"], filename=filename, secret=match,
                                 line_number=line_number, is_verified=is_verified)
            ps.check_id = self.regex_to_metadata[regex.pattern]["Check_ID"]  # type:ignore[attr-defined]
            if len(cast(str, ps.secret_value)) in range(MIN_CHARACTERS, MAX_CHARACTERS) or not regex_data['isCustom']:
                output.add(ps)
            else:
                logging.info(
                    f'Finding for check {ps.check_id} are not 5-100 characters in length, was ignored')  # type: ignore

        return output

    def analyze_string(self, string: str, **kwargs: Optional[Dict[str, Any]]) -> Generator[Tuple[str, Pattern[str]], None, None]:  # type:ignore[override]
        for regex in self.denylist:
            for match in regex.findall(string):
                if isinstance(match, tuple):
                    for submatch in filter(bool, match):
                        # It might make sense to paste break after yielding
                        yield submatch, regex
                else:
                    yield match, regex
