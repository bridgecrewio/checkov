from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from checkov.common.util.type_forcers import convert_csv_string_arg_to_list

if TYPE_CHECKING:
    from argparse import Namespace

logger = logging.getLogger(__name__)

# Severity codes that can be used for filtering
SEVERITY_CODES = {'CRITICAL', 'HIGH', 'MEDIUM', 'MODERATE', 'LOW', 'INFO', 'NONE'}

# Parameters that require an API key to function properly
API_KEY_REQUIRED_PARAMS = {
    'use_enforcement_rules': {
        'flag': '--use-enforcement-rules',
        'reason': 'Enforcement rules are fetched from Prisma Cloud platform'
    },
    'policy_metadata_filter': {
        'flag': '--policy-metadata-filter',
        'reason': 'Policy metadata filtering requires access to Prisma Cloud policy metadata'
    },
    'policy_metadata_filter_exception': {
        'flag': '--policy-metadata-filter-exception',
        'reason': 'Policy metadata filtering requires access to Prisma Cloud policy metadata'
    },
    'docker_image': {
        'flag': '--docker-image / --image',
        'reason': 'Docker image scanning requires platform integration'
    },
    'support': {
        'flag': '--support',
        'reason': 'Debug log upload requires platform integration'
    },
}

# Parameters that work better with an API key but can function without
API_KEY_ENHANCED_PARAMS = {
    'output_bc_ids': {
        'flag': '--output-bc-ids',
        'reason': 'Bridgecrew IDs are only available when connected to the platform'
    },
    'skip_download': {
        'flag': '--skip-download',
        'info': 'This flag prevents downloading metadata from Prisma Cloud (severities, guidelines, custom policies, etc.)'
    },
}


def check_for_severity_filtering_without_api_key(config: Namespace, has_api_key: bool) -> bool:
    """
    Check if the user is trying to filter by severity without an API key.
    
    :param config: The argparse Namespace configuration object
    :param has_api_key: Whether an API key is present
    :return: True if severity filtering was attempted without API key, False otherwise
    """
    if has_api_key:
        return False
    
    severity_filtering_attempted = False
    severity_codes_used = []
    
    # Check in --check parameter
    if hasattr(config, 'check') and config.check:
        check_list = convert_csv_string_arg_to_list(config.check)
        for check_id in check_list:
            if check_id.upper() in SEVERITY_CODES:
                severity_codes_used.append(f"--check {check_id}")
                severity_filtering_attempted = True
    
    # Check in --skip-check parameter
    if hasattr(config, 'skip_check') and config.skip_check:
        skip_check_list = convert_csv_string_arg_to_list(config.skip_check)
        for check_id in skip_check_list:
            if check_id.upper() in SEVERITY_CODES:
                severity_codes_used.append(f"--skip-check {check_id}")
                severity_filtering_attempted = True
    
    # Check in --hard-fail-on parameter
    if hasattr(config, 'hard_fail_on') and config.hard_fail_on:
        hard_fail_list = convert_csv_string_arg_to_list(config.hard_fail_on)
        for severity in hard_fail_list:
            if severity.upper() in SEVERITY_CODES:
                severity_codes_used.append(f"--hard-fail-on {severity}")
                severity_filtering_attempted = True
    
    # Check in --soft-fail-on parameter
    if hasattr(config, 'soft_fail_on') and config.soft_fail_on:
        soft_fail_list = convert_csv_string_arg_to_list(config.soft_fail_on)
        for severity in soft_fail_list:
            if severity.upper() in SEVERITY_CODES:
                severity_codes_used.append(f"--soft-fail-on {severity}")
                severity_filtering_attempted = True
    
    if severity_filtering_attempted:
        logger.warning(
            f"⚠️  Severity codes cannot be used without an API key:\n"
            f"   {', '.join(severity_codes_used)}\n"
            f"   \n"
            f"   Severity codes are not available without an API key because they come from the Prisma Cloud platform.\n"
            f"   Your filtering parameters using severity codes will be ignored during this scan.\n"
            f"   \n"
            f"   To enable severity-based filtering, provide an API key:\n"
            f"   --bc-api-key <your_key> or set BC_API_KEY environment variable"
        )
    
    return severity_filtering_attempted


def check_for_api_key_usage_warnings(config: Namespace, has_api_key: bool) -> None:
    """
    Check if the user is using parameters that require or are enhanced by an API key.
    Log appropriate warnings if no API key is provided.
    
    :param config: The argparse Namespace configuration object
    :param has_api_key: Whether an API key is present
    """
    if has_api_key:
        return
    
    warnings_logged = []
    
    # Check for severity-based filtering
    severity_warning_shown = check_for_severity_filtering_without_api_key(config, has_api_key)
    
    # Check for parameters that require an API key
    for param_name, param_info in API_KEY_REQUIRED_PARAMS.items():
        if hasattr(config, param_name) and getattr(config, param_name):
            logger.warning(
                f"⚠️  Parameter {param_info['flag']} requires an API key to function properly. "
                f"Reason: {param_info['reason']}. "
                f"Use --bc-api-key to provide a Bridgecrew or Prisma Cloud API key."
            )
            warnings_logged.append(param_info['flag'])
    
    # Check for parameters that are enhanced by an API key
    for param_name, param_info in API_KEY_ENHANCED_PARAMS.items():
        if hasattr(config, param_name) and getattr(config, param_name):
            if 'reason' in param_info:
                logger.info(
                    f"ℹ️  Parameter {param_info['flag']} works better with an API key. "
                    f"{param_info['reason']}"
                )
            elif 'info' in param_info:
                logger.info(f"ℹ️  {param_info['info']}")
            warnings_logged.append(param_info['flag'])
    
    # General info message if any warnings were logged (excluding severity warning which has its own message)
    if warnings_logged and not severity_warning_shown:
        logger.info(
            f"\n💡 To get full functionality, provide an API key using: "
            f"--bc-api-key <your_key> or set BC_API_KEY environment variable.\n"
            f"   For Prisma Cloud: --bc-api-key <access_key>::<secret_key> --prisma-api-url <your_prisma_url>"
        )


def warn_about_missing_metadata_without_api_key(has_api_key: bool) -> None:
    """
    Warn users that without an API key, they won't have access to:
    - Severity information
    - Policy guidelines
    - Bridgecrew IDs
    - Custom policies from the platform
    - Policy suppressions from the platform
    
    :param has_api_key: Whether an API key is present
    """
    if not has_api_key:
        logger.info(
            "\n📋 Running without API key - Limited metadata available:\n"
            "   • Severity levels will be estimated based on check categories\n"
            "   • Policy guidelines links may not be available\n"
            "   • Custom policies from platform will not be included\n"
            "   • Platform-based suppressions will not be applied\n"
            "   \n"
            "   💡 For full metadata and custom policies, use: --bc-api-key <your_key>"
        )
