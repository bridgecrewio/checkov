import pytest
from checkov.common.bridgecrew.severities import Severities
from checkov.policies_3d.runner import Policy3dRunner
from checkov.policies_3d.checks_parser import Policy3dParser
from checkov.common.bridgecrew.integration_features.features.policies_3d_integration import Policies3DIntegration


def test_runner_single_policy(policy_3d_1, scan_reports):
    # given
    checks = []
    parser = Policy3dParser()
    policies = [policy_3d_1]
    for policy in policies:
        converted_check = Policies3DIntegration._convert_raw_check(policy)
        check = parser.parse_raw_check(converted_check)
        check.severity = Severities[policy['severity']]
        check.bc_id = check.id
        checks.append(check)

    # when
    report = Policy3dRunner().run(checks=checks, scan_reports=scan_reports)

    # then
    assert len(report.failed_checks) == 1
    assert len(report.parsing_errors) == 0
    assert len(report.passed_checks) == 0
    assert len(report.skipped_checks) == 0


def test_runner_single_policy(policy_3d_1, scan_reports):
    # given
    checks = []
    parser = Policy3dParser()
    policies = [policy_3d_1]
    for policy in policies:
        converted_check = Policies3DIntegration._convert_raw_check(policy)
        check = parser.parse_raw_check(converted_check)
        check.severity = Severities[policy['severity']]
        check.bc_id = check.id
        checks.append(check)

    # when
    report = Policy3dRunner().run(checks=checks, scan_reports=scan_reports)

    # then
    assert len(report.failed_checks) == 1
    assert len(report.parsing_errors) == 0
    assert len(report.passed_checks) == 0
    assert len(report.skipped_checks) == 0


def test_runner_multi_policy(policy_3d_1, policy_3d_2, scan_reports):
    # given
    checks = []
    parser = Policy3dParser()
    policies = [policy_3d_1, policy_3d_2]
    for policy in policies:
        converted_check = Policies3DIntegration._convert_raw_check(policy)
        check = parser.parse_raw_check(converted_check)
        check.severity = Severities[policy['severity']]
        check.bc_id = check.id
        checks.append(check)

    # when
    report = Policy3dRunner().run(checks=checks, scan_reports=scan_reports)

    # then
    assert len(report.failed_checks) == 2
    assert len(report.parsing_errors) == 0
    assert len(report.passed_checks) == 0
    assert len(report.skipped_checks) == 0


def test_runner_multi_iac_checks_policy(policy_3d_3, scan_reports):
    # given
    checks = []
    parser = Policy3dParser()
    policies = [policy_3d_3]
    for policy in policies:
        converted_check = Policies3DIntegration._convert_raw_check(policy)
        check = parser.parse_raw_check(converted_check)
        check.severity = Severities[policy['severity']]
        check.bc_id = check.id
        checks.append(check)

    # when
    report = Policy3dRunner().run(checks=checks, scan_reports=scan_reports)

    # then
    assert len(report.failed_checks) == 1
    assert len(report.parsing_errors) == 0
    assert len(report.passed_checks) == 0
    assert len(report.skipped_checks) == 0
