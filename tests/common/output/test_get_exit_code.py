import os
import unittest

from checkov.common.bridgecrew.severities import BcSeverities, Severities
from checkov.common.models.enums import CheckResult
from checkov.common.output.report import Report
from checkov.common.output.record import Record
from checkov.common.util.consts import PARSE_ERROR_FAIL_FLAG


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

        # When soft_fail_on=['check1', 'check2'], exit code should be 0 if the only failing checks are in the
        # soft_fail_on list
        positive_test_soft_fail_on_code = r.get_exit_code(None, soft_fail_on=['CKV_AWS_157', 'CKV_AWS_16'],
                                                          hard_fail_on=None)
        positive_test_soft_fail_on_code_one_sev = r.get_exit_code(None, soft_fail_on=['LOW', 'CKV_AWS_16'],
                                                          hard_fail_on=None)
        positive_test_soft_fail_on_code_two_sev = r.get_exit_code(None, soft_fail_on=['LOW', 'HIGH'],
                                                                  hard_fail_on=None)
        positive_test_soft_fail_on_code_bc_id = r.get_exit_code(None, soft_fail_on=['BC_AWS_157', 'BC_AWS_16'],
                                                                hard_fail_on=None)

        negative_test_soft_fail_on_code = r.get_exit_code(None, soft_fail_on=['CKV_AWS_157'], hard_fail_on=None)
        negative_test_soft_fail_on_code_one_sev = r.get_exit_code(None, soft_fail_on=['LOW'], hard_fail_on=None)
        negative_test_soft_fail_on_code_bc_id = r.get_exit_code(None, soft_fail_on=['BC_AWS_157'], hard_fail_on=None)

        positive_test_soft_fail_on_wildcard_code = r.get_exit_code(None, soft_fail_on=['CKV_AWS*'])
        positive_test_soft_fail_on_wildcard_code_bc_id = r.get_exit_code(None, soft_fail_on=['BC_AWS*'])

        negative_test_soft_fail_on_wildcard_code = r.get_exit_code(None, soft_fail_on=['CKV_OTHER*'])
        negative_test_soft_fail_on_wildcard_code_bc_id = r.get_exit_code(None, soft_fail_on=['BC_OTHER*'])

        # When hard_fail_on=['check1', 'check2'], exit code should be 1 if any checks in the hard_fail_on list fail
        positive_test_hard_fail_on_code = r.get_exit_code(None, soft_fail_on=None, hard_fail_on=['CKV_AWS_157'])
        positive_test_hard_fail_on_code_one_sev = r.get_exit_code(None, soft_fail_on=None, hard_fail_on=['LOW'])
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
        self.assertEqual(positive_test_soft_fail_on_code, 0)
        self.assertEqual(positive_test_soft_fail_on_code_one_sev, 0)
        self.assertEqual(positive_test_soft_fail_on_code_two_sev, 0)
        self.assertEqual(positive_test_soft_fail_on_code_bc_id, 0)
        self.assertEqual(negative_test_soft_fail_on_code, 1)
        self.assertEqual(negative_test_soft_fail_on_code_one_sev, 1)
        self.assertEqual(negative_test_soft_fail_on_code_bc_id, 1)

        self.assertEqual(positive_test_soft_fail_on_wildcard_code, 0)
        self.assertEqual(positive_test_soft_fail_on_wildcard_code_bc_id, 0)
        self.assertEqual(negative_test_soft_fail_on_wildcard_code, 1)
        self.assertEqual(negative_test_soft_fail_on_wildcard_code_bc_id, 1)

        self.assertEqual(positive_test_hard_fail_on_code, 1)
        self.assertEqual(positive_test_hard_fail_on_code_one_sev, 1)
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


if __name__ == '__main__':
    unittest.main()
