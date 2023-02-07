from __future__ import annotations

import logging
from typing import Any, Dict, List
import yaml

from checkov.common.bridgecrew.platform_integration import bc_integration
from checkov.common.util.file_utils import decompress_file_gzip_base64


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
    logging.debug(f"(modify_secrets_policy_to_detectors) len secrets_list = {len(secrets_list)}")
    return secrets_list


def add_to_custom_detectors(custom_detectors: List[Dict[str, Any]], name: str, check_id: str, regex: str,
                            is_custom: str, is_multiline: bool = False) -> None:
    custom_detectors.append({
        'Name': name,
        'Check_ID': check_id,
        'Regex': regex,
        'isCustom': is_custom,
        'isMultiline': is_multiline
    })


def add_detectors_from_condition_query(custom_detectors: List[Dict[str, Any]], condition_query: Dict[str, Any],
                                       secret_policy: Dict[str, Any], check_id: str) -> bool:
    parsed = False
    cond_type = condition_query['cond_type']
    if cond_type == 'secrets':
        value = condition_query['value']
        if type(value) is str:
            value = [value]
        for regex in value:
            parsed = True
            add_to_custom_detectors(custom_detectors, secret_policy['title'], check_id, regex,
                                    secret_policy['isCustom'])
    return parsed


def add_detectors_from_code(custom_detectors: List[Dict[str, Any]], code: str, secret_policy: Dict[str, Any],
                            check_id: str) -> bool:
    parsed = False
    code_dict = yaml.safe_load(code)
    if 'definition' in code_dict:
        if 'value' in code_dict['definition'] and 'is_runnable' not in code_dict['definition']:
            parsed = True
            if type(code_dict['definition']['value']) is str:
                code_dict['definition']['value'] = [code_dict['definition']['value']]
            for regex in code_dict['definition']['value']:
                add_to_custom_detectors(
                    custom_detectors,
                    secret_policy['title'],
                    check_id,
                    regex,
                    secret_policy['isCustom'],
                    code_dict['definition'].get("multiline", False)
                )
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


def get_runnable_plugins(policies: List[Dict[str, Any]]) -> Dict[str, str]:
    runnables: dict[str, str] = {}
    for policy in policies:
        code = policy['code']
        if code:
            try:
                code_dict = yaml.safe_load(code)
                if 'definition' in code_dict:
                    if 'is_runnable' in code_dict['definition'] and 'value' in code_dict['definition']:
                        encoded_payload = code_dict['definition']['value']
                        if isinstance(encoded_payload, list):
                            encoded_payload = encoded_payload[0]
                        decoded_payload = decompress_file_gzip_base64(encoded_payload)
                        name: str = policy['title']
                        runnables[name] = decoded_payload.decode('utf8')
            except Exception as e:
                logging.warning(f"Could not parse runnable policy {policy['title']} due to: {e}")
    return runnables
