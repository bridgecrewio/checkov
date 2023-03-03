import argparse

import pytest

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.runners.runner_registry import RunnerRegistry


@pytest.mark.parametrize(
    "soft_fail,soft_fail_checks,hard_fail_checks,expected_exit_code",
    [
        (True, [], ['Valid'], 0),  # Soft fail overrides any check-specific definition
        (True, ['Invalid'], ['Valid'], 0),  # Soft fail overrides any check-specific definition
        (False, [], ['Valid'], 1),  # Hard fail on valid
        (False, ['Valid'], ['Valid'], 1),  # Hard fail check wins same soft fail check
        (False, [], ['Invalid'], 1),  # Hard fail on invalid
        (False, [], ['Unknown'], 1),  # Hard fail on unknown
        (False, ['Invalid', 'Valid', 'Unknown'], [], 0),  # Implicit soft fail on all statuses
        (True, [], ['Invalid', 'Valid', 'Unknown'], 0),  # Soft fail wins Implicit hard fail on all statuses
        (False, [], ['Invalid', 'Valid', 'Unknown'], 1),  # Implicit hard fail on all statuses
        (False, [], [], 1),  # default
        (True, [], [], 0)  # soft fail
    ],
)
def test_secrets_get_exit_code(secrets_report, soft_fail, soft_fail_checks, hard_fail_checks, expected_exit_code) -> None:
    exit_code_thresholds = {'soft_fail': soft_fail, 'soft_fail_checks': soft_fail_checks,
                            'soft_fail_threshold': None, 'hard_fail_checks': hard_fail_checks,
                            'hard_fail_threshold': None}

    assert secrets_report.get_exit_code(exit_code_thresholds) == expected_exit_code


@pytest.mark.parametrize(
    "soft_fail,soft_fail_on,hard_fail_on,expected_soft_fail_checks,expected_hard_fail_checks",
    [
        (False, None, None, [], []),  # default
        (False, 'invalid', None, ['Invalid'], []),  # assigning correct casing
        (False, 'invalid,valid,unknown', 'invalid,valid,unknown', ['Invalid', 'Valid', 'Unknown'], ['Invalid', 'Valid', 'Unknown'])  # assigning correct casing
    ]
)
def test_secrets_get_fail_threshold(soft_fail, soft_fail_on, hard_fail_on,
                                    expected_soft_fail_checks, expected_hard_fail_checks) -> None:
    config = argparse.Namespace(
        soft_fail=soft_fail,
        soft_fail_on=soft_fail_on,
        hard_fail_on=hard_fail_on,
        use_enforcement_rules=False
    )

    expected = {
        'soft_fail': soft_fail,
        'soft_fail_checks': expected_soft_fail_checks,
        'soft_fail_threshold': None,
        'hard_fail_checks': expected_hard_fail_checks,
        'hard_fail_threshold': None
    }

    assert RunnerRegistry.get_fail_thresholds(config, report_type=CheckType.SECRETS) == expected
