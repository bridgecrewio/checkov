import os
import unittest
from collections import defaultdict

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.bridgecrew.code_categories import CodeCategoryType, CodeCategoryConfiguration
from checkov.common.bridgecrew.severities import Severities, BcSeverities, Severity
from checkov.common.sast.consts import SastLanguages
from checkov.main import Checkov
from checkov.runner_filter import RunnerFilter


class TestRunnerFilter(unittest.TestCase):

    # Expected pseudo-code for when checks should run:
    #    if has_check_flag_specified():
    #        checks_to_run = checks_specifically_included
    #    else:
    #        checks_to_run = all_built_in_checks
    #    if has_checks_dir_specified():
    #       checks_to_run += checks_from_external_dir
    #    for skipped_check in skip_check_flags():
    #        checks_to_run.remove(skipped_check)

    def test_should_run_default(self):
        instance = RunnerFilter()
        self.assertTrue(instance.should_run_check(check_id="CHECK_1"))

    def test_should_run_specific_enable(self):
        instance = RunnerFilter(checks=["CHECK_1"])
        self.assertTrue(instance.should_run_check(check_id="CHECK_1"))

    def test_should_run_specific_enable_bc(self):
        instance = RunnerFilter(checks=["BC_CHECK_1"])
        self.assertTrue(instance.should_run_check(check_id="CHECK_1", bc_check_id="BC_CHECK_1"))

    def test_should_run_wildcard_enable(self):
        instance = RunnerFilter(checks=["CHECK_*"])
        self.assertTrue(instance.should_run_check(check_id="CHECK_1"))

    def test_should_run_wildcard_enable_bc(self):
        instance = RunnerFilter(checks=["BC_CHECK_*"])
        self.assertTrue(instance.should_run_check(check_id="CHECK_1", bc_check_id="BC_CHECK_1"))

    def test_should_run_omitted_specific_enable(self):
        instance = RunnerFilter(checks=["CHECK_1"])
        self.assertFalse(instance.should_run_check(check_id="CHECK_999"))

    def test_should_run_omitted_specific_enable_bc_id(self):
        instance = RunnerFilter(checks=["BC_CHECK_1"])
        self.assertFalse(instance.should_run_check(check_id="CHECK_999", bc_check_id="BC_CHECK_999"))

    def test_should_run_specific_disable(self):
        instance = RunnerFilter(skip_checks=["CHECK_1"])
        self.assertFalse(instance.should_run_check(check_id="CHECK_1"))

    def test_should_run_specific_disable_bc_id(self):
        instance = RunnerFilter(skip_checks=["BC_CHECK_1"])
        self.assertFalse(instance.should_run_check(check_id="CHECK_1", bc_check_id="BC_CHECK_1"))

    def test_should_run_omitted_specific_disable(self):
        instance = RunnerFilter(skip_checks=["CHECK_1"])
        self.assertTrue(instance.should_run_check(check_id="CHECK_999"))

    def test_should_run_omitted_specific_disable_bc_id(self):
        instance = RunnerFilter(skip_checks=["BC_CHECK_1"])
        self.assertTrue(instance.should_run_check(check_id="CHECK_999", bc_check_id="BC_CHECK_999"))

    def test_should_run_external(self):
        instance = RunnerFilter(skip_checks=["CHECK_1"])
        instance.notify_external_check("EXT_CHECK_999")
        self.assertTrue(instance.should_run_check(check_id="EXT_CHECK_999"))

    def test_should_run_external2(self):
        instance = RunnerFilter(checks=["CHECK_1"], skip_checks=["CHECK_2"])
        instance.notify_external_check("EXT_CHECK_999")
        self.assertFalse(instance.should_run_check(check_id="EXT_CHECK_999"))

    def test_should_run_external3(self):
        instance = RunnerFilter(checks=["EXT_CHECK_999"])
        instance.notify_external_check("EXT_CHECK_999")
        self.assertTrue(instance.should_run_check(check_id="EXT_CHECK_999"))

    def test_should_run_external4(self):
        instance = RunnerFilter(checks=["CHECK_1"], skip_checks=["CHECK_2"], all_external=True)
        instance.notify_external_check("EXT_CHECK_999")
        self.assertTrue(instance.should_run_check(check_id="EXT_CHECK_999"))

    def test_should_run_external_severity(self):
        instance = RunnerFilter(checks=["CHECK_1"], skip_checks=["CHECK_2", "HIGH"], all_external=True)
        instance.notify_external_check("EXT_CHECK_999")
        self.assertFalse(instance.should_run_check(check_id="EXT_CHECK_999", severity=Severities[BcSeverities.HIGH]))

    def test_should_run_external_disabled(self):
        instance = RunnerFilter(skip_checks=["CHECK_1", "EXT_CHECK_999"])
        instance.notify_external_check("EXT_CHECK_999")
        self.assertFalse(instance.should_run_check(check_id="EXT_CHECK_999"))

    def test_should_run_external_disabled2(self):
        instance = RunnerFilter(skip_checks=["CHECK_1", "EXT_CHECK_999"], all_external=True)
        instance.notify_external_check("EXT_CHECK_999")
        self.assertFalse(instance.should_run_check(check_id="EXT_CHECK_999"))

    def test_should_run_specific_disable_AND_enable(self):
        instance = RunnerFilter(checks=["CHECK_1"], skip_checks=["CHECK_1"])
        # prioritze disable - also this is not valid input and would be blocked in main.py
        self.assertFalse(instance.should_run_check(check_id="CHECK_1"))

    def test_should_run_omitted_wildcard(self):
        instance = RunnerFilter(skip_checks=["CHECK_AWS*"])
        self.assertTrue(instance.should_run_check(check_id="CHECK_999"))

    def test_should_run_omitted_wildcard_bc_id(self):
        instance = RunnerFilter(skip_checks=["BC_CHECK_AWS*"])
        self.assertTrue(instance.should_run_check(check_id="CHECK_999", bc_check_id="BC_CHECK_999"))

    def test_should_run_omitted_wildcard2(self):
        instance = RunnerFilter(skip_checks=["CHECK_AWS*"])
        self.assertFalse(instance.should_run_check(check_id="CHECK_AWS_909"))

    def test_should_run_omitted_wildcard2_bc_id(self):
        instance = RunnerFilter(skip_checks=["BC_CHECK_AWS*"])
        self.assertFalse(instance.should_run_check(check_id="CHECK_AWS_909", bc_check_id="BC_CHECK_AWS_909"))

    def test_should_run_omitted_wildcard3(self):
        instance = RunnerFilter(skip_checks=["CHECK_AWS*","CHECK_AZURE*"])
        self.assertTrue(instance.should_run_check(check_id="EXT_CHECK_909"))

    def test_should_run_omitted_wildcard4(self):
        instance = RunnerFilter(skip_checks=["CHECK_AWS*","CHECK_AZURE_01"])
        self.assertFalse(instance.should_run_check(check_id="CHECK_AZURE_01"))

    def test_should_run_severity1(self):
        instance = RunnerFilter(checks=["LOW"])
        self.assertTrue(instance.should_run_check(check_id='', severity=Severities[BcSeverities.LOW]))

    def test_should_run_severity1_lowercase(self):
        instance = RunnerFilter(checks=["low"])
        self.assertTrue(instance.should_run_check(check_id='', severity=Severities[BcSeverities.LOW]))

    def test_should_run_severity2(self):
        instance = RunnerFilter(skip_checks=["LOW"])
        self.assertTrue(instance.should_run_check(check_id='', severity=Severities[BcSeverities.HIGH]))

    def test_should_run_severity2_lowercase(self):
        instance = RunnerFilter(skip_checks=["low"])
        self.assertTrue(instance.should_run_check(check_id='', severity=Severities[BcSeverities.HIGH]))

    def test_should_skip_severity1(self):
        instance = RunnerFilter(checks=["HIGH"])
        self.assertFalse(instance.should_run_check(check_id='', severity=Severities[BcSeverities.LOW]))

    def test_should_skip_severity1_lowercase(self):
        instance = RunnerFilter(checks=["high"])
        self.assertFalse(instance.should_run_check(check_id='', severity=Severities[BcSeverities.LOW]))

    def test_should_skip_severity2(self):
        instance = RunnerFilter(skip_checks=["LOW"])
        self.assertFalse(instance.should_run_check(check_id='', severity=Severities[BcSeverities.LOW]))

    def test_should_skip_severity2_lowercase(self):
        instance = RunnerFilter(skip_checks=["low"])
        self.assertFalse(instance.should_run_check(check_id='', severity=Severities[BcSeverities.LOW]))

    def test_should_run_check_id(self):
        instance = RunnerFilter(checks=['CKV_AWS_45'])
        from checkov.terraform.checks.resource.aws.LambdaEnvironmentCredentials import check
        self.assertTrue(instance.should_run_check(check=check))

    def test_should_run_check_id_omitted(self):
        instance = RunnerFilter(checks=['CKV_AWS_99'])
        from checkov.terraform.checks.resource.aws.LambdaEnvironmentCredentials import check
        self.assertFalse(instance.should_run_check(check=check))

    def test_should_run_check_bc_id(self):
        instance = RunnerFilter(checks=['BC_AWS_45'])
        from checkov.terraform.checks.resource.aws.LambdaEnvironmentCredentials import check
        check.bc_id = 'BC_AWS_45'
        self.assertTrue(instance.should_run_check(check=check))

    def test_should_run_check_bc_id_omitted(self):
        instance = RunnerFilter(checks=['BC_AWS_99'])
        from checkov.terraform.checks.resource.aws.LambdaEnvironmentCredentials import check
        check.bc_id = 'BC_AWS_45'
        self.assertFalse(instance.should_run_check(check=check))

    def test_should_skip_check_id(self):
        instance = RunnerFilter(skip_checks=['CKV_AWS_45'])
        from checkov.terraform.checks.resource.aws.LambdaEnvironmentCredentials import check
        self.assertFalse(instance.should_run_check(check=check))

    def test_should_skip_check_id_omitted(self):
        instance = RunnerFilter(skip_checks=['CKV_AWS_99'])
        from checkov.terraform.checks.resource.aws.LambdaEnvironmentCredentials import check
        self.assertTrue(instance.should_run_check(check=check))

    def test_should_skip_check_bc_id(self):
        instance = RunnerFilter(skip_checks=['BC_AWS_45'])
        from checkov.terraform.checks.resource.aws.LambdaEnvironmentCredentials import check
        check.bc_id = 'BC_AWS_45'
        self.assertFalse(instance.should_run_check(check=check))

    def test_should_skip_check_bc_id_omitted(self):
        instance = RunnerFilter(skip_checks=['BC_AWS_99'])
        from checkov.terraform.checks.resource.aws.LambdaEnvironmentCredentials import check
        check.bc_id = 'BC_AWS_45'
        self.assertTrue(instance.should_run_check(check=check))

    def test_should_run_check_severity(self):
        instance = RunnerFilter(checks=['LOW'])
        from checkov.terraform.checks.resource.aws.LambdaEnvironmentCredentials import check
        check.severity = Severities[BcSeverities.LOW]
        self.assertTrue(instance.should_run_check(check=check))

    def test_should_run_check_severity_omitted(self):
        instance = RunnerFilter(checks=['HIGH'])
        from checkov.terraform.checks.resource.aws.LambdaEnvironmentCredentials import check
        check.severity = Severities[BcSeverities.LOW]
        self.assertFalse(instance.should_run_check(check=check))

    def test_should_run_check_severity_implicit(self):
        instance = RunnerFilter(checks=['LOW'])
        from checkov.terraform.checks.resource.aws.LambdaEnvironmentCredentials import check
        check.severity = Severities[BcSeverities.HIGH]
        self.assertTrue(instance.should_run_check(check=check))

    def test_should_skip_check_severity(self):
        instance = RunnerFilter(skip_checks=['LOW'])
        from checkov.terraform.checks.resource.aws.LambdaEnvironmentCredentials import check
        check.severity = Severities[BcSeverities.LOW]
        self.assertFalse(instance.should_run_check(check=check))

    def test_should_skip_check_severity_implicit(self):
        instance = RunnerFilter(skip_checks=['HIGH'])
        from checkov.terraform.checks.resource.aws.LambdaEnvironmentCredentials import check
        check.severity = Severities[BcSeverities.LOW]
        self.assertFalse(instance.should_run_check(check=check))

    def test_should_skip_check_severity_threshold_exceeded(self):
        instance = RunnerFilter(skip_checks=['LOW'])
        from checkov.terraform.checks.resource.aws.LambdaEnvironmentCredentials import check
        check.severity = Severities[BcSeverities.HIGH]
        self.assertTrue(instance.should_run_check(check=check))

    def test_check_severity_split_no_sev(self):
        instance = RunnerFilter(checks=['XYZ'])
        self.assertIsNone(instance.check_threshold)
        self.assertEqual(instance.checks, ['XYZ'])

    def test_check_severity_split_skip_no_sev(self):
        instance = RunnerFilter(skip_checks=['XYZ'])
        self.assertIsNone(instance.skip_check_threshold)
        self.assertEqual(instance.skip_checks, ['XYZ'])

    def test_check_severity_split_one_sev(self):
        instance = RunnerFilter(checks=['MEDIUM'])
        self.assertEqual(instance.check_threshold, Severities[BcSeverities.MEDIUM])
        self.assertEqual(instance.checks, [])

    def test_check_severity_split_two_sev(self):
        instance = RunnerFilter(checks=['MEDIUM', 'LOW'])
        # should take the lowest severity
        self.assertEqual(instance.check_threshold, Severities[BcSeverities.LOW])
        self.assertEqual(instance.checks, [])

    def test_check_severity_split_two_sev_lowercase(self):
        instance = RunnerFilter(checks=['MEDIUM', 'low'])
        # should take the lowest severity
        self.assertEqual(instance.check_threshold, Severities[BcSeverities.LOW])
        self.assertEqual(instance.checks, [])

    def test_check_severity_split_skip_one_sev(self):
        instance = RunnerFilter(skip_checks=['MEDIUM'])
        self.assertEqual(instance.skip_check_threshold, Severities[BcSeverities.MEDIUM])
        self.assertEqual(instance.skip_checks, [])

    def test_check_severity_split_skip_two_sev(self):
        instance = RunnerFilter(skip_checks=['LOW', 'MEDIUM'])
        # should take the highest severity
        self.assertEqual(instance.skip_check_threshold, Severities[BcSeverities.MEDIUM])
        self.assertEqual(instance.skip_checks, [])

    def test_check_severity_split_skip_two_sev_lowercase(self):
        instance = RunnerFilter(skip_checks=['LOW', 'medium'])
        # should take the highest severity
        self.assertEqual(instance.skip_check_threshold, Severities[BcSeverities.MEDIUM])
        self.assertEqual(instance.skip_checks, [])

    def test_run_sev_id_1(self):
        instance = RunnerFilter(checks=['HIGH'], skip_checks=['CKV_AWS_123'])
        # run all high and above, but skip this one ID regardless of severity
        self.assertTrue(instance.should_run_check(check_id='CKV_AWS_789', severity=Severities[BcSeverities.HIGH]))
        self.assertTrue(instance.should_run_check(check_id='CKV_AWS_789', severity=Severities[BcSeverities.CRITICAL]))
        self.assertFalse(instance.should_run_check(check_id='CKV_AWS_789', severity=Severities[BcSeverities.LOW]))
        self.assertFalse(instance.should_run_check(check_id='CKV_AWS_123', severity=Severities[BcSeverities.HIGH]))
        self.assertFalse(instance.should_run_check(check_id='CKV_AWS_123', severity=Severities[BcSeverities.CRITICAL]))

    def test_run_sev_no_check_sev(self):
        instance = RunnerFilter(checks=['HIGH'])
        # if a check severity is used, skip any check without it
        self.assertFalse(instance.should_run_check(check_id='CKV_AWS_789'))

    def test_run_sev_no_check_sev_with_id(self):
        instance = RunnerFilter(checks=['HIGH', 'CKV_AWS_789'])
        # if a check severity is used, skip any check without it
        self.assertTrue(instance.should_run_check(check_id='CKV_AWS_789'))

    def test_skip_sev_no_check_sev(self):
        instance = RunnerFilter(skip_checks=['HIGH'])
        # if a skip check severity is used, run any check without it
        self.assertTrue(instance.should_run_check(check_id='CKV_AWS_789'))

    def test_skip_sev_no_check_sev_with_id(self):
        instance = RunnerFilter(skip_checks=['HIGH', 'CKV_AWS_789'])
        # if a skip check severity is used, run any check without it
        self.assertFalse(instance.should_run_check(check_id='CKV_AWS_789'))

    def test_run_sev_id_2(self):
        instance = RunnerFilter(checks=['CKV_AWS_123'], skip_checks=['MEDIUM'])
        # Run AWS_123, unless it is MEDIUM or below
        self.assertFalse(instance.should_run_check(check_id='CKV_AWS_789', severity=Severities[BcSeverities.CRITICAL]))
        self.assertFalse(instance.should_run_check(check_id='CKV_AWS_789', severity=Severities[BcSeverities.HIGH]))
        self.assertTrue(instance.should_run_check(check_id='CKV_AWS_123', severity=Severities[BcSeverities.CRITICAL]))
        self.assertTrue(instance.should_run_check(check_id='CKV_AWS_123', severity=Severities[BcSeverities.HIGH]))
        self.assertFalse(instance.should_run_check(check_id='CKV_AWS_123', severity=Severities[BcSeverities.MEDIUM]))
        self.assertFalse(instance.should_run_check(check_id='CKV_AWS_123', severity=Severities[BcSeverities.LOW]))

    def test_run_two_sev_1(self):
        instance = RunnerFilter(checks=['MEDIUM'], skip_checks=['HIGH'])
        # run medium and higher, skip high and lower; skip takes priority
        self.assertFalse(instance.should_run_check(check_id='CKV_AWS_789', severity=Severities[BcSeverities.HIGH]))
        self.assertTrue(instance.should_run_check(check_id='CKV_AWS_789', severity=Severities[BcSeverities.CRITICAL]))
        self.assertFalse(instance.should_run_check(check_id='CKV_AWS_789', severity=Severities[BcSeverities.LOW]))
        self.assertFalse(instance.should_run_check(check_id='CKV_AWS_123', severity=Severities[BcSeverities.MEDIUM]))

    def test_run_two_sev_2(self):
        instance = RunnerFilter(checks=['HIGH'], skip_checks=['MEDIUM'])
        # run HIGH and higher, skip MEDIUM and lower (so just run HIGH or higher)
        self.assertTrue(instance.should_run_check(check_id='CKV_AWS_789', severity=Severities[BcSeverities.HIGH]))
        self.assertTrue(instance.should_run_check(check_id='CKV_AWS_789', severity=Severities[BcSeverities.CRITICAL]))
        self.assertFalse(instance.should_run_check(check_id='CKV_AWS_789', severity=Severities[BcSeverities.LOW]))
        self.assertFalse(instance.should_run_check(check_id='CKV_AWS_123', severity=Severities[BcSeverities.MEDIUM]))

    def test_run_sev_explicit(self):
        instance = RunnerFilter(checks=['MEDIUM', 'CKV_AWS_789'])
        self.assertTrue(instance.should_run_check(check_id='CKV_AWS_789', severity=Severities[BcSeverities.LOW]))
        self.assertFalse(instance.should_run_check(check_id='CKV_AWS_123', severity=Severities[BcSeverities.LOW]))
        self.assertTrue(instance.should_run_check(check_id='CKV_AWS_123', severity=Severities[BcSeverities.HIGH]))

    def test_skip_sev_explicit(self):
        instance = RunnerFilter(skip_checks=['MEDIUM', 'CKV_AWS_789'])
        self.assertFalse(instance.should_run_check(check_id='CKV_AWS_789', severity=Severities[BcSeverities.HIGH]))
        self.assertFalse(instance.should_run_check(check_id='CKV_AWS_123', severity=Severities[BcSeverities.LOW]))
        self.assertTrue(instance.should_run_check(check_id='CKV_AWS_123', severity=Severities[BcSeverities.HIGH]))

    def test_within_threshold(self):
        instance = RunnerFilter(checks=['LOW'])
        self.assertTrue(instance.within_threshold(Severities[BcSeverities.LOW]))
        self.assertTrue(instance.within_threshold(Severities[BcSeverities.MEDIUM]))

        instance = RunnerFilter(checks=['HIGH'])
        self.assertFalse(instance.within_threshold(Severities[BcSeverities.LOW]))
        self.assertFalse(instance.within_threshold(Severities[BcSeverities.MEDIUM]))

        instance = RunnerFilter(skip_checks=['HIGH'])
        self.assertFalse(instance.within_threshold(Severities[BcSeverities.LOW]))
        self.assertFalse(instance.within_threshold(Severities[BcSeverities.MEDIUM]))

        instance = RunnerFilter(skip_checks=['LOW'])
        self.assertFalse(instance.within_threshold(Severities[BcSeverities.LOW]))
        self.assertTrue(instance.within_threshold(Severities[BcSeverities.MEDIUM]))

        instance = RunnerFilter(checks=['HIGH'], skip_checks=['LOW'])
        self.assertFalse(instance.within_threshold(Severities[BcSeverities.LOW]))
        self.assertFalse(instance.within_threshold(Severities[BcSeverities.MEDIUM]))
        self.assertTrue(instance.within_threshold(Severities[BcSeverities.HIGH]))

    def test_within_threshold_special_severities(self):
        instance = RunnerFilter(skip_checks=['MEDIUM'])
        self.assertFalse(instance.within_threshold(Severities[BcSeverities.LOW]))
        self.assertFalse(instance.within_threshold(Severities[BcSeverities.MODERATE]))
        self.assertTrue(instance.within_threshold(Severities[BcSeverities.HIGH]))
        instance = RunnerFilter(skip_checks=['HIGH'])
        self.assertFalse(instance.within_threshold(Severities[BcSeverities.LOW]))
        self.assertFalse(instance.within_threshold(Severities[BcSeverities.MEDIUM]))
        self.assertFalse(instance.within_threshold(Severities[BcSeverities.IMPORTANT]))
        self.assertTrue(instance.within_threshold(Severities[BcSeverities.CRITICAL]))

    def test_include_local_skip_local(self):
        instance = RunnerFilter(include_all_checkov_policies=False)
        self.assertFalse(instance.should_run_check(check_id='CKV_AWS_789'))

    def test_include_local_run_local(self):
        instance = RunnerFilter(include_all_checkov_policies=True)
        self.assertTrue(instance.should_run_check(check_id='CKV_AWS_789'))

    def test_include_local_skip_platform(self):
        instance = RunnerFilter(include_all_checkov_policies=False)
        self.assertTrue(instance.should_run_check(check_id='CKV_AWS_789', bc_check_id='BC_AWS_789'))

    def test_include_local_run_platform(self):
        instance = RunnerFilter(include_all_checkov_policies=True)
        self.assertTrue(instance.should_run_check(check_id='CKV_AWS_789', bc_check_id='BC_AWS_789'))

    def test_include_local_skip_custom(self):
        instance = RunnerFilter(include_all_checkov_policies=False)
        instance.notify_external_check("EXT_CHECK_999")
        self.assertTrue(instance.should_run_check(check_id='EXT_CHECK_999'))

    def test_include_local_run_custom(self):
        instance = RunnerFilter(include_all_checkov_policies=True)
        instance.notify_external_check("EXT_CHECK_999")
        self.assertTrue(instance.should_run_check(check_id='EXT_CHECK_999'))

    def test_include_local_skip_local_explicit_run(self):
        instance = RunnerFilter(checks=['CKV_AWS_789'], include_all_checkov_policies=False)
        self.assertTrue(instance.should_run_check(check_id='CKV_AWS_789'))

    def test_include_local_skip_local_implicit_run(self):
        instance = RunnerFilter(skip_checks=['CKV_AWS_123'], include_all_checkov_policies=False)
        self.assertFalse(instance.should_run_check(check_id='CKV_AWS_789'))

    def test_include_local_skip_local_severity(self):
        # this case should not actually be possible (no severities if not a platform check), but testing the logic anyways
        instance = RunnerFilter(checks=['HIGH'], include_all_checkov_policies=False)
        self.assertFalse(instance.should_run_check(check_id='CKV_AWS_789', severity=Severities[BcSeverities.HIGH]))

    def test_should_run_only_filtered_policies(self):
        instance = RunnerFilter(checks=['HIGH'], include_all_checkov_policies=False,
                                filtered_policy_ids=["NOT_CKV_AWS_789"])
        self.assertFalse(instance.should_run_check(check_id='CKV_AWS_789', severity=Severities[BcSeverities.HIGH]))

    def test_should_skip_explicit_run_if_not_filtered(self):
        instance = RunnerFilter(checks=['CKV_AWS_789'], include_all_checkov_policies=False,
                                filtered_policy_ids=["NOT_CKV_AWS_789"])
        self.assertFalse(instance.should_run_check(check_id='CKV_AWS_789'))

    def test_should_skip_filtered_policy(self):
        instance = RunnerFilter(skip_checks=['CKV_AWS_789'], include_all_checkov_policies=False,
                                filtered_policy_ids=["CKV_AWS_789"])
        self.assertFalse(instance.should_run_check(check_id='CKV_AWS_789'))

    def test_should_run_if_no_filtered_policies(self):
        instance = RunnerFilter(checks=['CKV_AWS_789'], include_all_checkov_policies=False,
                                filtered_policy_ids=[])
        self.assertTrue(instance.should_run_check(check_id='CKV_AWS_789'))

    def test_should_skip_explicit_run_if_policy_exception(self):
        instance = RunnerFilter(checks=['CKV_AWS_789'], include_all_checkov_policies=False,
                                filtered_exception_policy_ids=['CKV_AWS_789'])
        self.assertFalse(instance.should_run_check(check_id='CKV_AWS_789'))

    def test_should_skip_policy_exception(self):
        instance = RunnerFilter(skip_checks=['CKV_AWS_789'], include_all_checkov_policies=False,
                                filtered_exception_policy_ids=["CKV_AWS_789"])
        self.assertFalse(instance.should_run_check(check_id='CKV_AWS_789'))

    def test_should_run_if_no_policy_exceptions(self):
        instance = RunnerFilter(checks=['CKV_AWS_789'], include_all_checkov_policies=False,
                                filtered_exception_policy_ids=[])
        self.assertTrue(instance.should_run_check(check_id='CKV_AWS_789'))

    def test_should_skip_if_filtered_policy_is_also_policy_exception(self):
        instance = RunnerFilter(checks=['CKV_AWS_789'], include_all_checkov_policies=False,
                                filtered_policy_ids=['CKV_AWS_789'], filtered_exception_policy_ids=['CKV_AWS_789'])
        self.assertFalse(instance.should_run_check(check_id='CKV_AWS_789'))

    def test_should_run_check_enforcement_rules(self):
        instance = RunnerFilter(include_all_checkov_policies=True,
                                filtered_policy_ids=[], use_enforcement_rules=True)

        enforcement_rule_configs = {
            CodeCategoryType.IAC: CodeCategoryConfiguration(CodeCategoryType.IAC, Severities[BcSeverities.MEDIUM], Severities[BcSeverities.MEDIUM]),
             CodeCategoryType.SECRETS: CodeCategoryConfiguration(CodeCategoryType.SECRETS, Severities[BcSeverities.HIGH], Severities[BcSeverities.HIGH]),
            CodeCategoryType.WEAKNESSES: CodeCategoryConfiguration(CodeCategoryType.WEAKNESSES, Severities[BcSeverities.HIGH],Severities[BcSeverities.HIGH]),
            CodeCategoryType.BUILD_INTEGRITY: CodeCategoryConfiguration(CodeCategoryType.BUILD_INTEGRITY, Severities[BcSeverities.MEDIUM], Severities[BcSeverities.HIGH]),
            CodeCategoryType.LICENSES: CodeCategoryConfiguration(CodeCategoryType.LICENSES, Severities[BcSeverities.MEDIUM], Severities[BcSeverities.HIGH]),
            CodeCategoryType.VULNERABILITIES: CodeCategoryConfiguration(CodeCategoryType.VULNERABILITIES, Severities[BcSeverities.HIGH], Severities[BcSeverities.HIGH])
        }

        instance.apply_enforcement_rules(enforcement_rule_configs)

        self.assertTrue(instance.should_run_check(check_id='CKV_AWS_789', severity=Severities[BcSeverities.MEDIUM], report_type=CheckType.TERRAFORM))
        self.assertFalse(instance.should_run_check(check_id='CKV_AWS_789', severity=Severities[BcSeverities.MEDIUM], report_type=CheckType.SECRETS))
        self.assertFalse(instance.should_run_check(check_id='CKV_AWS_789', severity=Severities[BcSeverities.LOW], report_type=CheckType.TERRAFORM))
        self.assertFalse(instance.should_run_check(check_id='CKV_AWS_789', severity=Severities[BcSeverities.LOW], report_type=CheckType.SECRETS))

    def test_should_run_check_enforcement_rules_explicit_checks(self):
        instance = RunnerFilter(include_all_checkov_policies=True, checks=['CKV_AWS_789'],
                                filtered_policy_ids=[], use_enforcement_rules=True)

        enforcement_rule_configs = {
            CodeCategoryType.IAC: CodeCategoryConfiguration(CodeCategoryType.IAC, Severities[BcSeverities.MEDIUM], Severities[BcSeverities.MEDIUM]),
            CodeCategoryType.SECRETS: CodeCategoryConfiguration(CodeCategoryType.SECRETS, Severities[BcSeverities.HIGH], Severities[BcSeverities.HIGH]),
            CodeCategoryType.WEAKNESSES: CodeCategoryConfiguration(CodeCategoryType.WEAKNESSES, Severities[BcSeverities.HIGH], Severities[BcSeverities.HIGH]),
            CodeCategoryType.BUILD_INTEGRITY: CodeCategoryConfiguration(CodeCategoryType.BUILD_INTEGRITY, Severities[BcSeverities.MEDIUM], Severities[BcSeverities.HIGH]),
            CodeCategoryType.LICENSES: CodeCategoryConfiguration(CodeCategoryType.LICENSES, Severities[BcSeverities.MEDIUM], Severities[BcSeverities.HIGH]),
            CodeCategoryType.VULNERABILITIES: CodeCategoryConfiguration(CodeCategoryType.VULNERABILITIES, Severities[BcSeverities.HIGH], Severities[BcSeverities.HIGH])
        }

        instance.apply_enforcement_rules(enforcement_rule_configs)

        # hardcoded check IDs always run (if not removed by --skip-check)
        self.assertTrue(instance.should_run_check(check_id='CKV_AWS_789', severity=Severities[BcSeverities.MEDIUM], report_type=CheckType.TERRAFORM))
        self.assertTrue(instance.should_run_check(check_id='CKV_AWS_789', severity=Severities[BcSeverities.MEDIUM], report_type=CheckType.SECRETS))
        self.assertTrue(instance.should_run_check(check_id='CKV_AWS_789', severity=Severities[BcSeverities.LOW], report_type=CheckType.TERRAFORM))
        self.assertTrue(instance.should_run_check(check_id='CKV_AWS_789', severity=Severities[BcSeverities.LOW], report_type=CheckType.SECRETS))
        # these run based on severity
        self.assertTrue(instance.should_run_check(check_id='CKV_AWS_123', severity=Severities[BcSeverities.MEDIUM], report_type=CheckType.TERRAFORM))
        self.assertFalse(instance.should_run_check(check_id='CKV_AWS_123', severity=Severities[BcSeverities.MEDIUM], report_type=CheckType.SECRETS))
        self.assertFalse(instance.should_run_check(check_id='CKV_AWS_123', severity=Severities[BcSeverities.LOW], report_type=CheckType.TERRAFORM))
        self.assertFalse(instance.should_run_check(check_id='CKV_AWS_123', severity=Severities[BcSeverities.LOW], report_type=CheckType.SECRETS))

    def test_should_run_check_enforcement_rules_explicit_skip_checks(self):
        instance = RunnerFilter(include_all_checkov_policies=True, skip_checks=['CKV_AWS_789'],
                                filtered_policy_ids=[], use_enforcement_rules=True)

        enforcement_rule_configs = {
            CodeCategoryType.IAC: CodeCategoryConfiguration(CodeCategoryType.IAC, Severities[BcSeverities.MEDIUM], Severities[BcSeverities.MEDIUM]),
            CodeCategoryType.SECRETS: CodeCategoryConfiguration(CodeCategoryType.SECRETS, Severities[BcSeverities.HIGH], Severities[BcSeverities.HIGH]),
            CodeCategoryType.WEAKNESSES: CodeCategoryConfiguration(CodeCategoryType.WEAKNESSES, Severities[BcSeverities.HIGH], Severities[BcSeverities.HIGH]),
            CodeCategoryType.BUILD_INTEGRITY: CodeCategoryConfiguration(CodeCategoryType.BUILD_INTEGRITY, Severities[BcSeverities.MEDIUM], Severities[BcSeverities.HIGH]),
            CodeCategoryType.LICENSES: CodeCategoryConfiguration(CodeCategoryType.LICENSES, Severities[BcSeverities.MEDIUM], Severities[BcSeverities.HIGH]),
            CodeCategoryType.VULNERABILITIES: CodeCategoryConfiguration(CodeCategoryType.VULNERABILITIES, Severities[BcSeverities.HIGH], Severities[BcSeverities.HIGH])
        }

        instance.apply_enforcement_rules(enforcement_rule_configs)

        # the logic is to merge the skip check with the enforcement rule setting, if all the skip-checks are IDs (not severities)
        # so we always skip 789, and run 123 based on the severity
        self.assertFalse(instance.should_run_check(check_id='CKV_AWS_789', severity=Severities[BcSeverities.MEDIUM], report_type=CheckType.TERRAFORM))
        self.assertFalse(instance.should_run_check(check_id='CKV_AWS_789', severity=Severities[BcSeverities.MEDIUM], report_type=CheckType.SECRETS))
        self.assertFalse(instance.should_run_check(check_id='CKV_AWS_789', severity=Severities[BcSeverities.LOW], report_type=CheckType.TERRAFORM))
        self.assertFalse(instance.should_run_check(check_id='CKV_AWS_789', severity=Severities[BcSeverities.LOW], report_type=CheckType.SECRETS))
        self.assertTrue(instance.should_run_check(check_id='CKV_AWS_123', severity=Severities[BcSeverities.MEDIUM], report_type=CheckType.TERRAFORM))
        self.assertFalse(instance.should_run_check(check_id='CKV_AWS_123', severity=Severities[BcSeverities.MEDIUM], report_type=CheckType.SECRETS))
        self.assertFalse(instance.should_run_check(check_id='CKV_AWS_123', severity=Severities[BcSeverities.LOW], report_type=CheckType.TERRAFORM))
        self.assertFalse(instance.should_run_check(check_id='CKV_AWS_123', severity=Severities[BcSeverities.LOW], report_type=CheckType.SECRETS))

    def test_should_run_check_enforcement_rules_skip_severity(self):
        instance = RunnerFilter(include_all_checkov_policies=True, skip_checks=['MEDIUM'],
                                filtered_policy_ids=[], use_enforcement_rules=True)

        enforcement_rule_configs = {
            CodeCategoryType.IAC: CodeCategoryConfiguration(CodeCategoryType.IAC, Severities[BcSeverities.MEDIUM], Severities[BcSeverities.MEDIUM]),
            CodeCategoryType.SECRETS: CodeCategoryConfiguration(CodeCategoryType.SECRETS, Severities[BcSeverities.HIGH], Severities[BcSeverities.HIGH]),
            CodeCategoryType.WEAKNESSES: CodeCategoryConfiguration(CodeCategoryType.WEAKNESSES, Severities[BcSeverities.HIGH], Severities[BcSeverities.HIGH]),
            CodeCategoryType.BUILD_INTEGRITY: CodeCategoryConfiguration(CodeCategoryType.BUILD_INTEGRITY, Severities[BcSeverities.MEDIUM], Severities[BcSeverities.HIGH]),
            CodeCategoryType.LICENSES: CodeCategoryConfiguration(CodeCategoryType.LICENSES, Severities[BcSeverities.MEDIUM], Severities[BcSeverities.HIGH]),
            CodeCategoryType.VULNERABILITIES: CodeCategoryConfiguration(CodeCategoryType.VULNERABILITIES, Severities[BcSeverities.HIGH], Severities[BcSeverities.HIGH])
        }

        instance.apply_enforcement_rules(enforcement_rule_configs)

        # the skip_check severity value just totally overrides the enforcement rule
        self.assertFalse(instance.should_run_check(check_id='CKV_AWS_789', severity=Severities[BcSeverities.MEDIUM], report_type=CheckType.TERRAFORM))
        self.assertFalse(instance.should_run_check(check_id='CKV_AWS_789', severity=Severities[BcSeverities.MEDIUM], report_type=CheckType.SECRETS))
        self.assertFalse(instance.should_run_check(check_id='CKV_AWS_789', severity=Severities[BcSeverities.LOW], report_type=CheckType.TERRAFORM))
        self.assertFalse(instance.should_run_check(check_id='CKV_AWS_789', severity=Severities[BcSeverities.LOW], report_type=CheckType.SECRETS))
        self.assertTrue(instance.should_run_check(check_id='CKV_AWS_123', severity=Severities[BcSeverities.HIGH], report_type=CheckType.TERRAFORM))
        self.assertTrue(instance.should_run_check(check_id='CKV_AWS_123', severity=Severities[BcSeverities.HIGH], report_type=CheckType.SECRETS))
        self.assertTrue(instance.should_run_check(check_id='CKV_AWS_123', severity=Severities[BcSeverities.HIGH], report_type=CheckType.TERRAFORM))
        self.assertTrue(instance.should_run_check(check_id='CKV_AWS_123', severity=Severities[BcSeverities.HIGH], report_type=CheckType.SECRETS))

    def test_should_run_check_enforcement_rules_run_severity(self):
        instance = RunnerFilter(include_all_checkov_policies=True, checks=['MEDIUM'],
                                filtered_policy_ids=[], use_enforcement_rules=True)

        enforcement_rule_configs = {
            CodeCategoryType.IAC: CodeCategoryConfiguration(CodeCategoryType.IAC, Severities[BcSeverities.MEDIUM], Severities[BcSeverities.MEDIUM]),
            CodeCategoryType.SECRETS: CodeCategoryConfiguration(CodeCategoryType.SECRETS, Severities[BcSeverities.HIGH], Severities[BcSeverities.HIGH]),
            CodeCategoryType.WEAKNESSES: CodeCategoryConfiguration(CodeCategoryType.WEAKNESSES, Severities[BcSeverities.HIGH], Severities[BcSeverities.HIGH]),
            CodeCategoryType.BUILD_INTEGRITY: CodeCategoryConfiguration(CodeCategoryType.BUILD_INTEGRITY, Severities[BcSeverities.MEDIUM], Severities[BcSeverities.HIGH]),
            CodeCategoryType.LICENSES: CodeCategoryConfiguration(CodeCategoryType.LICENSES, Severities[BcSeverities.MEDIUM], Severities[BcSeverities.HIGH]),
            CodeCategoryType.VULNERABILITIES: CodeCategoryConfiguration(CodeCategoryType.VULNERABILITIES, Severities[BcSeverities.HIGH], Severities[BcSeverities.HIGH])
        }

        instance.apply_enforcement_rules(enforcement_rule_configs)

        # use of --check with a severity overrides the enforcement rule (so just run all MEDIUM+)
        self.assertTrue(instance.should_run_check(check_id='CKV_AWS_789', severity=Severities[BcSeverities.MEDIUM], report_type=CheckType.TERRAFORM))
        self.assertTrue(instance.should_run_check(check_id='CKV_AWS_789', severity=Severities[BcSeverities.MEDIUM], report_type=CheckType.SECRETS))
        self.assertFalse(instance.should_run_check(check_id='CKV_AWS_789', severity=Severities[BcSeverities.LOW], report_type=CheckType.TERRAFORM))
        self.assertFalse(instance.should_run_check(check_id='CKV_AWS_789', severity=Severities[BcSeverities.LOW], report_type=CheckType.SECRETS))
        self.assertTrue(instance.should_run_check(check_id='CKV_AWS_123', severity=Severities[BcSeverities.HIGH], report_type=CheckType.TERRAFORM))
        self.assertTrue(instance.should_run_check(check_id='CKV_AWS_123', severity=Severities[BcSeverities.HIGH], report_type=CheckType.SECRETS))
        self.assertTrue(instance.should_run_check(check_id='CKV_AWS_123', severity=Severities[BcSeverities.HIGH], report_type=CheckType.TERRAFORM))
        self.assertTrue(instance.should_run_check(check_id='CKV_AWS_123', severity=Severities[BcSeverities.HIGH], report_type=CheckType.SECRETS))

    def test_should_run_check_enforcement_rules_run_and_skip_id(self):
        instance = RunnerFilter(include_all_checkov_policies=True, checks=['CKV_AWS_123'], skip_checks=['CKV_AWS_789'],
                                filtered_policy_ids=[], use_enforcement_rules=True)

        enforcement_rule_configs = {
            CodeCategoryType.IAC: CodeCategoryConfiguration(CodeCategoryType.IAC, Severities[BcSeverities.MEDIUM], Severities[BcSeverities.MEDIUM]),
            CodeCategoryType.SECRETS: CodeCategoryConfiguration(CodeCategoryType.SECRETS, Severities[BcSeverities.HIGH], Severities[BcSeverities.HIGH]),
            CodeCategoryType.WEAKNESSES: CodeCategoryConfiguration(CodeCategoryType.WEAKNESSES, Severities[BcSeverities.HIGH], Severities[BcSeverities.HIGH]),
            CodeCategoryType.BUILD_INTEGRITY: CodeCategoryConfiguration(CodeCategoryType.BUILD_INTEGRITY, Severities[BcSeverities.MEDIUM], Severities[BcSeverities.HIGH]),
            CodeCategoryType.LICENSES: CodeCategoryConfiguration(CodeCategoryType.LICENSES, Severities[BcSeverities.MEDIUM], Severities[BcSeverities.HIGH]),
            CodeCategoryType.VULNERABILITIES: CodeCategoryConfiguration(CodeCategoryType.VULNERABILITIES, Severities[BcSeverities.HIGH], Severities[BcSeverities.HIGH])
        }

        instance.apply_enforcement_rules(enforcement_rule_configs)

        # run / skip based on ID lists
        self.assertFalse(instance.should_run_check(check_id='CKV_AWS_789', severity=Severities[BcSeverities.MEDIUM], report_type=CheckType.TERRAFORM))
        self.assertFalse(instance.should_run_check(check_id='CKV_AWS_789', severity=Severities[BcSeverities.MEDIUM], report_type=CheckType.SECRETS))
        self.assertFalse(instance.should_run_check(check_id='CKV_AWS_789', severity=Severities[BcSeverities.LOW], report_type=CheckType.TERRAFORM))
        self.assertFalse(instance.should_run_check(check_id='CKV_AWS_789', severity=Severities[BcSeverities.LOW], report_type=CheckType.SECRETS))
        self.assertTrue(instance.should_run_check(check_id='CKV_AWS_123', severity=Severities[BcSeverities.MEDIUM], report_type=CheckType.TERRAFORM))
        self.assertTrue(instance.should_run_check(check_id='CKV_AWS_123', severity=Severities[BcSeverities.MEDIUM], report_type=CheckType.SECRETS))
        self.assertTrue(instance.should_run_check(check_id='CKV_AWS_123', severity=Severities[BcSeverities.LOW], report_type=CheckType.TERRAFORM))
        self.assertTrue(instance.should_run_check(check_id='CKV_AWS_123', severity=Severities[BcSeverities.LOW], report_type=CheckType.SECRETS))

        # anything else is based on enforcement rule severity
        self.assertTrue(instance.should_run_check(check_id='CKV_AWS_456', severity=Severities[BcSeverities.MEDIUM], report_type=CheckType.TERRAFORM))
        self.assertFalse(instance.should_run_check(check_id='CKV_AWS_456', severity=Severities[BcSeverities.MEDIUM], report_type=CheckType.SECRETS))
        self.assertFalse(instance.should_run_check(check_id='CKV_AWS_456', severity=Severities[BcSeverities.LOW], report_type=CheckType.TERRAFORM))
        self.assertFalse(instance.should_run_check(check_id='CKV_AWS_456', severity=Severities[BcSeverities.LOW], report_type=CheckType.SECRETS))

    def test_should_run_check_enforcement_rules_run_id_skip_severity(self):
        instance = RunnerFilter(include_all_checkov_policies=True, checks=['CKV_AWS_123'], skip_checks=['MEDIUM'],
                                filtered_policy_ids=[], use_enforcement_rules=True)

        enforcement_rule_configs = {
            CodeCategoryType.IAC: CodeCategoryConfiguration(CodeCategoryType.IAC, Severities[BcSeverities.MEDIUM], Severities[BcSeverities.MEDIUM]),
            CodeCategoryType.SECRETS: CodeCategoryConfiguration(CodeCategoryType.SECRETS, Severities[BcSeverities.HIGH], Severities[BcSeverities.HIGH]),
            CodeCategoryType.WEAKNESSES: CodeCategoryConfiguration(CodeCategoryType.WEAKNESSES, Severities[BcSeverities.HIGH], Severities[BcSeverities.HIGH]),
            CodeCategoryType.BUILD_INTEGRITY: CodeCategoryConfiguration(CodeCategoryType.BUILD_INTEGRITY, Severities[BcSeverities.MEDIUM], Severities[BcSeverities.HIGH]),
            CodeCategoryType.LICENSES: CodeCategoryConfiguration(CodeCategoryType.LICENSES, Severities[BcSeverities.MEDIUM], Severities[BcSeverities.HIGH]),
            CodeCategoryType.VULNERABILITIES: CodeCategoryConfiguration(CodeCategoryType.VULNERABILITIES, Severities[BcSeverities.HIGH], Severities[BcSeverities.HIGH])
        }

        instance.apply_enforcement_rules(enforcement_rule_configs)

        # the presence of a severity in check/skip overrides enforcement rules, and 789 just gets implicitly skipped because it's not in the allow list
        self.assertFalse(instance.should_run_check(check_id='CKV_AWS_789', severity=Severities[BcSeverities.HIGH], report_type=CheckType.TERRAFORM))
        self.assertFalse(instance.should_run_check(check_id='CKV_AWS_789', severity=Severities[BcSeverities.MEDIUM], report_type=CheckType.SECRETS))
        self.assertFalse(instance.should_run_check(check_id='CKV_AWS_789', severity=Severities[BcSeverities.LOW], report_type=CheckType.TERRAFORM))
        self.assertFalse(instance.should_run_check(check_id='CKV_AWS_789', severity=Severities[BcSeverities.LOW], report_type=CheckType.SECRETS))
        self.assertTrue(instance.should_run_check(check_id='CKV_AWS_123', severity=Severities[BcSeverities.HIGH], report_type=CheckType.TERRAFORM))
        self.assertFalse(instance.should_run_check(check_id='CKV_AWS_123', severity=Severities[BcSeverities.MEDIUM], report_type=CheckType.SECRETS))
        self.assertFalse(instance.should_run_check(check_id='CKV_AWS_123', severity=Severities[BcSeverities.LOW], report_type=CheckType.TERRAFORM))
        self.assertFalse(instance.should_run_check(check_id='CKV_AWS_123', severity=Severities[BcSeverities.LOW], report_type=CheckType.SECRETS))

    def test_should_run_check_enforcement_rules_run_severity_skip_id(self):
        instance = RunnerFilter(include_all_checkov_policies=True, checks=['MEDIUM'], skip_checks=['CKV_AWS_123'],
                                filtered_policy_ids=[], use_enforcement_rules=True)

        enforcement_rule_configs = {
            CodeCategoryType.IAC: CodeCategoryConfiguration(CodeCategoryType.IAC, Severities[BcSeverities.MEDIUM], Severities[BcSeverities.MEDIUM]),
            CodeCategoryType.SECRETS: CodeCategoryConfiguration(CodeCategoryType.SECRETS, Severities[BcSeverities.HIGH], Severities[BcSeverities.HIGH]),
            CodeCategoryType.WEAKNESSES: CodeCategoryConfiguration(CodeCategoryType.WEAKNESSES, Severities[BcSeverities.HIGH], Severities[BcSeverities.HIGH]),
            CodeCategoryType.BUILD_INTEGRITY: CodeCategoryConfiguration(CodeCategoryType.BUILD_INTEGRITY, Severities[BcSeverities.MEDIUM], Severities[BcSeverities.HIGH]),
            CodeCategoryType.LICENSES: CodeCategoryConfiguration(CodeCategoryType.LICENSES, Severities[BcSeverities.MEDIUM], Severities[BcSeverities.HIGH]),
            CodeCategoryType.VULNERABILITIES: CodeCategoryConfiguration(CodeCategoryType.VULNERABILITIES, Severities[BcSeverities.HIGH], Severities[BcSeverities.HIGH])
        }

        instance.apply_enforcement_rules(enforcement_rule_configs)

        # the presence of a severity in check/skip overrides enforcement rules, so run 789 based on severity and always skip 123
        self.assertTrue(instance.should_run_check(check_id='CKV_AWS_789', severity=Severities[BcSeverities.HIGH], report_type=CheckType.TERRAFORM))
        self.assertTrue(instance.should_run_check(check_id='CKV_AWS_789', severity=Severities[BcSeverities.MEDIUM], report_type=CheckType.SECRETS))
        self.assertFalse(instance.should_run_check(check_id='CKV_AWS_789', severity=Severities[BcSeverities.LOW], report_type=CheckType.TERRAFORM))
        self.assertFalse(instance.should_run_check(check_id='CKV_AWS_789', severity=Severities[BcSeverities.LOW], report_type=CheckType.SECRETS))
        self.assertFalse(instance.should_run_check(check_id='CKV_AWS_123', severity=Severities[BcSeverities.HIGH], report_type=CheckType.TERRAFORM))
        self.assertFalse(instance.should_run_check(check_id='CKV_AWS_123', severity=Severities[BcSeverities.MEDIUM], report_type=CheckType.SECRETS))
        self.assertFalse(instance.should_run_check(check_id='CKV_AWS_123', severity=Severities[BcSeverities.LOW], report_type=CheckType.TERRAFORM))
        self.assertFalse(instance.should_run_check(check_id='CKV_AWS_123', severity=Severities[BcSeverities.LOW], report_type=CheckType.SECRETS))

    def test_extract_enforcement_rule_threshold(self):
        instance = RunnerFilter(include_all_checkov_policies=True, filtered_policy_ids=[], use_enforcement_rules=True)

        enforcement_rule_configs = {
            CodeCategoryType.IAC: CodeCategoryConfiguration(CodeCategoryType.IAC, Severities[BcSeverities.LOW], Severities[BcSeverities.LOW]),
            CodeCategoryType.BUILD_INTEGRITY: CodeCategoryConfiguration(CodeCategoryType.BUILD_INTEGRITY, Severities[BcSeverities.MEDIUM], Severities[BcSeverities.MEDIUM]),
            CodeCategoryType.LICENSES: CodeCategoryConfiguration(CodeCategoryType.LICENSES, Severities[BcSeverities.HIGH], Severities[BcSeverities.HIGH]),
            CodeCategoryType.VULNERABILITIES: CodeCategoryConfiguration(CodeCategoryType.VULNERABILITIES, Severities[BcSeverities.MEDIUM], Severities[BcSeverities.MEDIUM]),
            CodeCategoryType.SECRETS: CodeCategoryConfiguration(CodeCategoryType.SECRETS, Severities[BcSeverities.HIGH], Severities[BcSeverities.HIGH]),
            CodeCategoryType.WEAKNESSES: CodeCategoryConfiguration(CodeCategoryType.WEAKNESSES, Severities[BcSeverities.HIGH], Severities[BcSeverities.HIGH])
        }

        instance.apply_enforcement_rules(enforcement_rule_configs)

        self.assertEqual(instance.extract_enforcement_rule_threshold('BC_LIC_1', 'sca_package'), Severities[BcSeverities.HIGH])
        self.assertEqual(instance.extract_enforcement_rule_threshold('BC_PRISMA_2022_123', 'sca_package'), Severities[BcSeverities.MEDIUM])
        self.assertEqual(instance.extract_enforcement_rule_threshold('BC_CVE_2022_123', 'sca_package'), Severities[BcSeverities.MEDIUM])
        self.assertEqual(instance.extract_enforcement_rule_threshold('CKV_PRISMA_2022_123', 'sca_package'), Severities[BcSeverities.MEDIUM])
        self.assertEqual(instance.extract_enforcement_rule_threshold('CKV_CVE_2022_123', 'sca_package'), Severities[BcSeverities.MEDIUM])
        self.assertEqual(instance.extract_enforcement_rule_threshold('CKV_AWS_123', 'terraform'), Severities[BcSeverities.LOW])
        self.assertEqual(instance.extract_enforcement_rule_threshold('BC_AWS_123', 'terraform'), Severities[BcSeverities.LOW])

    def test_apply_enforcement_rules(self):
        instance = RunnerFilter(include_all_checkov_policies=True, filtered_policy_ids=[], use_enforcement_rules=True)

        enforcement_rule_configs = {
            CodeCategoryType.IAC: CodeCategoryConfiguration(CodeCategoryType.IAC, Severities[BcSeverities.LOW], Severities[BcSeverities.LOW]),
            CodeCategoryType.BUILD_INTEGRITY: CodeCategoryConfiguration(CodeCategoryType.BUILD_INTEGRITY, Severities[BcSeverities.INFO], Severities[BcSeverities.INFO]),
            CodeCategoryType.LICENSES: CodeCategoryConfiguration(CodeCategoryType.LICENSES, Severities[BcSeverities.HIGH], Severities[BcSeverities.HIGH]),
            CodeCategoryType.VULNERABILITIES: CodeCategoryConfiguration(CodeCategoryType.VULNERABILITIES, Severities[BcSeverities.MEDIUM], Severities[BcSeverities.MEDIUM]),
            CodeCategoryType.SECRETS: CodeCategoryConfiguration(CodeCategoryType.SECRETS, Severities[BcSeverities.OFF], Severities[BcSeverities.OFF]),
            CodeCategoryType.WEAKNESSES: CodeCategoryConfiguration(CodeCategoryType.WEAKNESSES, Severities[BcSeverities.OFF], Severities[BcSeverities.OFF])
        }

        instance.apply_enforcement_rules(enforcement_rule_configs)
        expected = {
            'ansible': Severities[BcSeverities.LOW],
            'argo_workflows': Severities[BcSeverities.INFO],
            'arm': Severities[BcSeverities.LOW],
            'azure_pipelines': Severities[BcSeverities.INFO],
            'bicep': Severities[BcSeverities.LOW],
            'bitbucket_pipelines': Severities[BcSeverities.INFO],
            'cdk': Severities[BcSeverities.OFF],
            'circleci_pipelines': Severities[BcSeverities.INFO],
            'cloudformation': Severities[BcSeverities.LOW],
            'dockerfile': Severities[BcSeverities.LOW],
            'github_configuration': Severities[BcSeverities.INFO],
            'github_actions': Severities[BcSeverities.INFO],
            'gitlab_configuration': Severities[BcSeverities.INFO],
            'gitlab_ci': Severities[BcSeverities.INFO],
            'bitbucket_configuration': Severities[BcSeverities.INFO],
            'helm': Severities[BcSeverities.LOW],
            'json': Severities[BcSeverities.LOW],
            'yaml': Severities[BcSeverities.LOW],
            'kubernetes': Severities[BcSeverities.LOW],
            'kustomize': Severities[BcSeverities.LOW],
            'openapi': Severities[BcSeverities.LOW],
            'sca_package': {
                CodeCategoryType.LICENSES: Severities[BcSeverities.HIGH],
                CodeCategoryType.VULNERABILITIES: Severities[BcSeverities.MEDIUM]
            },
            'sca_image': {
                CodeCategoryType.LICENSES: Severities[BcSeverities.HIGH],
                CodeCategoryType.VULNERABILITIES: Severities[BcSeverities.MEDIUM]
            },
            'secrets': Severities[BcSeverities.OFF],
            'serverless': Severities[BcSeverities.LOW],
            'terraform': Severities[BcSeverities.LOW],
            'terraform_json': Severities[BcSeverities.LOW],
            'terraform_plan': Severities[BcSeverities.LOW],
            '3d_policy': Severities[BcSeverities.LOW],
            'sast': Severities[BcSeverities.OFF],
            'sast_python': Severities[BcSeverities.OFF],
            'sast_java': Severities[BcSeverities.OFF],
            'sast_javascript': Severities[BcSeverities.OFF],
            'sast_typescript': Severities[BcSeverities.OFF],
            'sast_golang': Severities[BcSeverities.OFF],
        }
        self.assertEqual(instance.enforcement_rule_configs, expected)

    def test_resource_attr_to_omit_load_config_empty_list(self):
        runner_filter = RunnerFilter(resource_attr_to_omit=defaultdict(lambda: []))
        assert not runner_filter.resource_attr_to_omit
        # assert that we have default dict as well:
        runner_filter.resource_attr_to_omit["acab"].update(["ac", "ab"])
        assert len(runner_filter.resource_attr_to_omit["acab"]) == 2

    def test_should_not_skip_cloned_policy(self):
        instance = RunnerFilter(include_all_checkov_policies=True)
        instance.bc_cloned_checks = {'BC_GCP_NETWORKING_17': [
                                    [{'id': '1234567_GCP_9876543', 'code': 'null',
                                      'title': 'GCP Firewall rule allows all traffic on HTTP port (80)',
                                      'guideline': 'Refer the documentation for more details,\nhttps://docs.bridgecrew.io/docs/ensure-gcp-google-compute-firewall-ingress-does-not-allow-unrestricted-http-port-80-access',
                                      'severity': Severity(BcSeverities.HIGH, 4), 'pcSeverity': 'HIGH',
                                      'category': 'Networking', 'pcPolicyId': '123456-873b-4a71-91a8-41a42e4c9314',
                                      'additionalPcPolicyIds': ['123456-873b-4a71-91a8-41a42e4c9314'],
                                      'sourceIncidentId': 'BC_GCP_NETWORKING_17', 'benchmarks': {},
                                      'frameworks': ['CloudFormation', 'Terraform'], 'provider': 'GCP'}]]}
        instance.suppressed_policies = ['BC_GCP_NETWORKING_17']
        self.assertTrue(instance.should_run_check(check_id='CKV_GCP_106', bc_check_id='BC_GCP_NETWORKING_17'))

    def test_should_skip_suppressed_policy(self):
        instance = RunnerFilter(include_all_checkov_policies=True)
        instance.bc_cloned_checks = {'BC_GCP_NETWORKING_17': [
                                    [{'id': '1234567_GCP_9876543', 'code': 'null',
                                      'title': 'GCP Firewall rule allows all traffic on HTTP port (80)',
                                      'guideline': 'Refer the documentation for more details,\nhttps://docs.bridgecrew.io/docs/ensure-gcp-google-compute-firewall-ingress-does-not-allow-unrestricted-http-port-80-access',
                                      'severity': Severity(BcSeverities.HIGH, 4), 'pcSeverity': 'HIGH',
                                      'category': 'Networking', 'pcPolicyId': '123456-873b-4a71-91a8-41a42e4c9314',
                                      'additionalPcPolicyIds': ['123456-873b-4a71-91a8-41a42e4c9314'],
                                      'sourceIncidentId': 'BC_GCP_NETWORKING_17', 'benchmarks': {},
                                      'frameworks': ['CloudFormation', 'Terraform'], 'provider': 'GCP'}]]}
        instance.suppressed_policies = ['BC_GCP_NETWORKING_18']
        self.assertFalse(instance.should_run_check(check_id='CKV_GCP_77', bc_check_id='BC_GCP_NETWORKING_18'))


    def test_resource_attr_to_omit_load_config_sanity_absolute_path(self):
        """
        This check is more than a Sanity test - it also checks parser edge cases -
        - key has single str value
        - key has a list of values, one of them has incompatible type (first file content contains single str value
            in key3 & int value in key4. Both need to be parsed into a set)
        """
        first_file_real_parsed_content = {
            "aws_db_instance": {"storage_container_path"},
            "key2": {"storage_container_path"},
            "key3": {"admin_password"},
            "key4": {"admin_password", "1"},
            "key5": {"plaintext"},
            # ToDo: Uncomment if we want to support universal masking
            # "*": {"plaintext"}
        }

        argv = [
            "--config-file",
            f"{os.path.dirname(os.path.realpath(__file__))}/resource_attr_to_omit_configs/first.yml"
        ]
        ckv = Checkov(argv=argv)
        runner_filter = RunnerFilter(resource_attr_to_omit=ckv.config.mask)
        assert runner_filter.resource_attr_to_omit
        for k, v in runner_filter.resource_attr_to_omit.items():
            assert v == first_file_real_parsed_content.get(k)

        for k, v in first_file_real_parsed_content.items():
            assert v == runner_filter.resource_attr_to_omit.get(k)

    def test_resource_attr_to_omit_load_config_sanity_combine(self):
        combined_file_real_parsed_content = {
            "aws_db_instance": {"storage_container_path"},
            "key2": {"storage_container_path"},
            "key3": {"admin_password", "blabla"},
            "key4": {"admin_password", "blabla2", "1", "2"},
            "key5": {"plaintext", "admin_password"},
            "key6": {"admin_password"},
            "key7": {"plaintext"},
            # ToDo: Uncomment if we want to support universal masking
            # "*": {"plaintext"}
        }

        argv = [
            "--config-file",
            f"{os.path.dirname(os.path.realpath(__file__))}/resource_attr_to_omit_configs/combined.yml"
        ]
        ckv = Checkov(argv=argv)
        runner_filter = RunnerFilter(resource_attr_to_omit=ckv.config.mask)

        assert runner_filter.resource_attr_to_omit
        for k, v in runner_filter.resource_attr_to_omit.items():
            assert v == combined_file_real_parsed_content.get(k)

        for k, v in combined_file_real_parsed_content.items():
            assert v == runner_filter.resource_attr_to_omit.get(k)

    def test_get_sast_languages(self):
        sast_langs = RunnerFilter.get_sast_languages(['sast'], [])
        assert SastLanguages.PYTHON in sast_langs
        assert SastLanguages.JAVA in sast_langs
        assert SastLanguages.JAVASCRIPT in sast_langs
        assert SastLanguages.TYPESCRIPT in sast_langs
        assert SastLanguages.GOLANG in sast_langs
        sast_langs = RunnerFilter.get_sast_languages(['sast_python', 'sast_typescript', 'sast_golang'], [])
        assert SastLanguages.PYTHON in sast_langs
        assert SastLanguages.TYPESCRIPT in sast_langs
        assert SastLanguages.GOLANG in sast_langs
        sast_langs = RunnerFilter.get_sast_languages(['sast_python', 'sast_javascript'], [])
        assert SastLanguages.PYTHON in sast_langs
        assert SastLanguages.JAVASCRIPT in sast_langs
        sast_langs = RunnerFilter.get_sast_languages(['all'], [])
        assert all(lang in sast_langs for lang in SastLanguages)

        # skip
        sast_langs = RunnerFilter.get_sast_languages(['all'], ['sast_python', 'sast_javascript'])
        assert SastLanguages.JAVA in sast_langs
        assert SastLanguages.PYTHON not in sast_langs
        assert SastLanguages.JAVASCRIPT not in sast_langs
        assert SastLanguages.TYPESCRIPT in sast_langs
        assert SastLanguages.GOLANG in sast_langs

    def test_scan_secrets_history_limits_to_secrets_framework(self):
        # when
        filter = RunnerFilter(enable_git_history_secret_scan=True)

        # then
        assert filter.enable_git_history_secret_scan is True
        assert filter.framework == [CheckType.SECRETS]


if __name__ == '__main__':
    unittest.main()
