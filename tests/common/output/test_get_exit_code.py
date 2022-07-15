import argparse
import os
import unittest

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.bridgecrew.code_categories import CodeCategoryType, CodeCategoryConfiguration
from checkov.common.bridgecrew.integration_features.features.repo_config_integration import \
    integration as repo_config_integration
from checkov.common.bridgecrew.severities import BcSeverities, Severities
from checkov.common.models.enums import CheckResult
from checkov.common.output.report import Report
from checkov.common.output.record import Record
from checkov.common.runners.runner_registry import RunnerRegistry
from checkov.common.util.consts import PARSE_ERROR_FAIL_FLAG
from checkov.runner_filter import RunnerFilter


class TestGetExitCode(unittest.TestCase):

    def test_get_exit_code(self):
        record1 = Record(check_id='CKV_AWS_157',
                         bc_check_id='BC_AWS_157',
                         check_name="Some RDS check", check_result={"result": CheckResult.FAILED},
                         code_block=None, file_path="./rds.tf",
                         file_line_range='1:3',
                         resource='aws_db_instance.sample', evaluations=None,
                         check_class=None, file_abs_path=',.',
                         severity=Severities[BcSeverities.LOW],
                         entity_tags={
                             'tag1': 'value1'
                         })
        record2 = Record(check_id='CKV_AWS_16',
                         bc_check_id='BC_AWS_16',
                         check_name="Another RDS check",
                         check_result={"result": CheckResult.FAILED},
                         code_block=None, file_path="./rds.tf",
                         file_line_range='1:3',
                         resource='aws_db_instance.sample', evaluations=None,
                         check_class=None, file_abs_path=',.',
                         severity=Severities[BcSeverities.HIGH],
                         entity_tags={
                             'tag1': 'value1'
                         })

        record3 = Record(check_id='CKV_AWS_161',
                         bc_check_id='BC_AWS_161',
                         check_name="Another RDS check",
                         check_result={"result": CheckResult.PASSED},
                         code_block=None, file_path="./rds.tf",
                         file_line_range='1:3',
                         resource='aws_db_instance.sample', evaluations=None,
                         check_class=None, file_abs_path=',.',
                         severity=Severities[BcSeverities.LOW],
                         entity_tags={
                             'tag1': 'value1'
                         })
        record4 = Record(check_id='CKV_AWS_118',
                         bc_check_id='BC_AWS_118',
                         check_name="Another RDS check",
                         check_result={"result": CheckResult.PASSED},
                         code_block=None, file_path="./rds.tf",
                         file_line_range='1:3',
                         resource='aws_db_instance.sample', evaluations=None,
                         check_class=None, file_abs_path=',.',
                         severity=Severities[BcSeverities.HIGH],
                         entity_tags={
                             'tag1': 'value1'
                         })

        r = Report("terraform")
        r.add_record(record1)
        r.add_record(record2)
        r.add_record(record3)
        r.add_record(record4)

        # When soft_fail=True, the exit code should always be 0.
        test_default = r.get_exit_code(soft_fail=False, soft_fail_on=None, hard_fail_on=None)
        test_soft_fail = r.get_exit_code(soft_fail=True, soft_fail_on=None, hard_fail_on=None)
        test_hard_fail_off = r.get_exit_code(soft_fail=False, soft_fail_on=None, hard_fail_on=['OFF'])

        # When soft_fail_on=['check1', 'check2'], exit code should be 0 if the only failing checks are in the
        # soft_fail_on list
        positive_test_soft_fail_on_code = r.get_exit_code(None, soft_fail_on=['CKV_AWS_157', 'CKV_AWS_16'],
                                                          hard_fail_on=None)
        positive_test_soft_fail_on_code_one_sev = r.get_exit_code(None, soft_fail_on=['LOW', 'CKV_AWS_16'],
                                                          hard_fail_on=None)
        positive_test_soft_fail_on_code_one_sev_lowercase = r.get_exit_code(None, soft_fail_on=['low', 'CKV_AWS_16'],
                                                          hard_fail_on=None)
        positive_test_soft_fail_on_code_two_sev = r.get_exit_code(None, soft_fail_on=['LOW', 'HIGH'],
                                                                  hard_fail_on=None)
        positive_test_soft_fail_on_code_bc_id = r.get_exit_code(None, soft_fail_on=['BC_AWS_157', 'BC_AWS_16'],
                                                                hard_fail_on=None)

        negative_test_soft_fail_on_code = r.get_exit_code(None, soft_fail_on=['CKV_AWS_157'], hard_fail_on=None)
        negative_test_soft_fail_on_code_one_sev = r.get_exit_code(None, soft_fail_on=['LOW'], hard_fail_on=None)
        negative_test_soft_fail_on_code_one_sev_lowercase = r.get_exit_code(None, soft_fail_on=['low'], hard_fail_on=None)
        negative_test_soft_fail_on_code_bc_id = r.get_exit_code(None, soft_fail_on=['BC_AWS_157'], hard_fail_on=None)

        positive_test_soft_fail_on_wildcard_code = r.get_exit_code(None, soft_fail_on=['CKV_AWS*'])
        positive_test_soft_fail_on_wildcard_code_bc_id = r.get_exit_code(None, soft_fail_on=['BC_AWS*'])

        negative_test_soft_fail_on_wildcard_code = r.get_exit_code(None, soft_fail_on=['CKV_OTHER*'])
        negative_test_soft_fail_on_wildcard_code_bc_id = r.get_exit_code(None, soft_fail_on=['BC_OTHER*'])

        # When hard_fail_on=['check1', 'check2'], exit code should be 1 if any checks in the hard_fail_on list fail
        positive_test_hard_fail_on_code = r.get_exit_code(None, soft_fail_on=None, hard_fail_on=['CKV_AWS_157'])
        positive_test_hard_fail_on_code_one_sev = r.get_exit_code(None, soft_fail_on=None, hard_fail_on=['LOW'])
        positive_test_hard_fail_on_code_one_sev_lowercase = r.get_exit_code(None, soft_fail_on=None, hard_fail_on=['low'])
        positive_test_hard_fail_on_code_bc_id = r.get_exit_code(None, soft_fail_on=None, hard_fail_on=['BC_AWS_157'])

        negative_test_hard_fail_on_code = r.get_exit_code(None, soft_fail_on=None,
                                                          hard_fail_on=['CKV_AWS_161', 'CKV_AWS_118'])
        negative_test_hard_fail_on_code_bc_id = r.get_exit_code(None, soft_fail_on=None,
                                                                hard_fail_on=['BC_AWS_161', 'BC_AWS_118'])

        combined_test_soft_fail_sev_hard_fail_id = r.get_exit_code(None, soft_fail_on=['LOW', 'CKV_AWS_16'], hard_fail_on=['CKV_AWS_157'])
        combined_test_soft_fail_id_hard_fail_sev = r.get_exit_code(None, soft_fail_on=['CKV_AWS_16'], hard_fail_on=['HIGH'])
        combined_test_soft_fail_id_hard_fail_sev_fail = r.get_exit_code(True, soft_fail_on=['CKV_AWS_16'], hard_fail_on=['HIGH'])

        self.assertEqual(test_default, 1)
        self.assertEqual(test_soft_fail, 0)
        self.assertEqual(test_hard_fail_off, 0)
        self.assertEqual(positive_test_soft_fail_on_code, 0)
        self.assertEqual(positive_test_soft_fail_on_code_one_sev, 0)
        self.assertEqual(positive_test_soft_fail_on_code_one_sev_lowercase, 0)
        self.assertEqual(positive_test_soft_fail_on_code_two_sev, 0)
        self.assertEqual(positive_test_soft_fail_on_code_bc_id, 0)
        self.assertEqual(negative_test_soft_fail_on_code, 1)
        self.assertEqual(negative_test_soft_fail_on_code_one_sev, 1)
        self.assertEqual(negative_test_soft_fail_on_code_one_sev_lowercase, 1)
        self.assertEqual(negative_test_soft_fail_on_code_bc_id, 1)

        self.assertEqual(positive_test_soft_fail_on_wildcard_code, 0)
        self.assertEqual(positive_test_soft_fail_on_wildcard_code_bc_id, 0)
        self.assertEqual(negative_test_soft_fail_on_wildcard_code, 1)
        self.assertEqual(negative_test_soft_fail_on_wildcard_code_bc_id, 1)

        self.assertEqual(positive_test_hard_fail_on_code, 1)
        self.assertEqual(positive_test_hard_fail_on_code_one_sev, 1)
        self.assertEqual(positive_test_hard_fail_on_code_one_sev_lowercase, 1)
        self.assertEqual(positive_test_hard_fail_on_code_bc_id, 1)
        self.assertEqual(negative_test_hard_fail_on_code, 0)
        self.assertEqual(negative_test_hard_fail_on_code_bc_id, 0)

        self.assertEqual(combined_test_soft_fail_sev_hard_fail_id, 1)
        self.assertEqual(combined_test_soft_fail_id_hard_fail_sev, 1)
        self.assertEqual(combined_test_soft_fail_id_hard_fail_sev_fail, 0)

        os.environ[PARSE_ERROR_FAIL_FLAG] = 'true'
        r.add_parsing_error('some_file.tf')
        self.assertEqual(r.get_exit_code(soft_fail=False, soft_fail_on=None, hard_fail_on=None), 1)
        del os.environ[PARSE_ERROR_FAIL_FLAG]

    def test_get_fail_thresholds_enforcement_rules(self):

        old_configs = repo_config_integration.code_category_configs

        config = argparse.Namespace(
            use_platform_enforcement_rules=False,
            soft_fail=True,
            soft_fail_on=['MEDIUM'],
            hard_fail_on=['HIGH']
        )

        self.assertEqual(RunnerRegistry.get_fail_thresholds(config, report_type=CheckType.TERRAFORM), (True, ['MEDIUM'], ['HIGH']))

        repo_config_integration.code_category_configs = {
            CodeCategoryType.IAC: CodeCategoryConfiguration(CodeCategoryType.IAC, Severities[BcSeverities.MEDIUM], Severities[BcSeverities.CRITICAL])
        }
        config = argparse.Namespace(
            use_platform_enforcement_rules=True,
            soft_fail=False,
            soft_fail_on=None,
            hard_fail_on=None
        )
        # the soft-fail threshold is None because we will just let it be implicit based off hard fail (this is how enforcement rules works)
        self.assertEqual(RunnerRegistry.get_fail_thresholds(config, report_type=CheckType.TERRAFORM), (False, None, ['CRITICAL']))

        config = argparse.Namespace(
            use_platform_enforcement_rules=True,
            soft_fail=True,
            soft_fail_on=None,
            hard_fail_on=None
        )
        self.assertEqual(RunnerRegistry.get_fail_thresholds(config, report_type=CheckType.TERRAFORM), (True, None, ['CRITICAL']))

        config = argparse.Namespace(
            use_platform_enforcement_rules=True,
            soft_fail=True,
            soft_fail_on=['MEDIUM'],
            hard_fail_on=None
        )
        # here it is going to use in the actual value from the CLI option
        self.assertEqual(RunnerRegistry.get_fail_thresholds(config, report_type=CheckType.TERRAFORM), (True, ['MEDIUM'], ['CRITICAL']))

        config = argparse.Namespace(
            use_platform_enforcement_rules=True,
            soft_fail=True,
            soft_fail_on=['MEDIUM'],
            hard_fail_on=['HIGH']
        )
        self.assertEqual(RunnerRegistry.get_fail_thresholds(config, report_type=CheckType.TERRAFORM), (True, ['MEDIUM'], ['HIGH']))

        config = argparse.Namespace(
            use_platform_enforcement_rules=True,
            soft_fail=True,
            soft_fail_on=['CKV_AWS_123'],
            hard_fail_on=['CKV_AWS_789']
        )
        # it doesn't matter if we use check IDs or severities; either way it overrides enforcement rules
        self.assertEqual(RunnerRegistry.get_fail_thresholds(config, report_type=CheckType.TERRAFORM), (True, ['CKV_AWS_123'], ['CKV_AWS_789']))

        repo_config_integration.code_category_configs = {
            CodeCategoryType.IAC: CodeCategoryConfiguration(CodeCategoryType.IAC, Severities[BcSeverities.LOW], Severities[BcSeverities.OFF])
        }
        config = argparse.Namespace(
            use_platform_enforcement_rules=True,
            soft_fail=False,
            soft_fail_on=None,
            hard_fail_on=None
        )
        # This is a global soft fail from enforcement rules
        self.assertEqual(RunnerRegistry.get_fail_thresholds(config, report_type=CheckType.TERRAFORM), (True, None, ['OFF']))

        repo_config_integration.code_category_configs = old_configs


if __name__ == '__main__':
    unittest.main()
