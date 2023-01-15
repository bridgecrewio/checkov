import pytest


@pytest.mark.parametrize(
    "soft_fail,soft_fail_checks,hard_fail_checks,expected_exit_code",
    [
        (True, [], ['valid'], 0),  # Soft fail overrides any check-specific definition
        (True, ['invalid'], ['valid'], 0),  # Soft fail overrides any check-specific definition
        (False, [], ['valid'], 1),  # Hard fail on valid
        (False, ['valid'], ['valid'], 1),  # Hard fail check wins same soft fail check
        (False, [], ['invalid'], 1),  # Hard fail on invalid
        (False, [], ['unknown'], 1),  # Hard fail on unknown
        (False, ['invalid', 'valid', 'unknown'], [], 0),  # Implicit soft fail on all statuses
        (True, [], ['invalid', 'valid', 'unknown'], 0),  # Soft fail wins Implicit hard fail on all statuses
        (False, [], ['invalid', 'valid', 'unknown'], 1),  # Implicit hard fail on all statuses
        (False, [], [], 1),  # default
        (True, [], [], 0)  # soft fail
    ],
)
def test_secrets_get_exit_code(secrets_report, soft_fail, soft_fail_checks, hard_fail_checks, expected_exit_code) -> None:
    exit_code_thresholds = {'soft_fail': soft_fail, 'soft_fail_checks': soft_fail_checks,
                            'soft_fail_threshold': None, 'hard_fail_checks': hard_fail_checks,
                            'hard_fail_threshold': None}

    assert secrets_report.get_exit_code(exit_code_thresholds) == expected_exit_code
