import os
import unittest

from checkov.runner_filter import RunnerFilter
from checkov.terraform.runner import Runner
from checkov.terraform.checks.resource.alicloud.SecurityGroupUnrestrictedIngress22 import check


class TestSecurityGroupUnrestrictedIngress22(unittest.TestCase):

    def test(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = os.path.join(current_dir, "example_AbsSecurityGroupUnrestrictedIngress")
        report = runner.run(root_folder=test_files_dir,
                            runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            'alicloud_security_group_rule.allow_all_high',
            'alicloud_security_group_rule.allow_all_dns',
            'alicloud_security_group_rule.allow_all_http',
            'alicloud_security_group_rule.allow_all_ftp',
            'alicloud_security_group_rule.allow_all_ftpdata',
            'alicloud_security_group_rule.allow_all_mssqlmonitor',
            'alicloud_security_group_rule.allow_all_mssql',
            'alicloud_security_group_rule.allow_all_mysql',
            'alicloud_security_group_rule.allow_all_oracledb',
            'alicloud_security_group_rule.allow_all_postgresql',
            'alicloud_security_group_rule.allow_all_rdp',
            'alicloud_security_group_rule.allow_all_smtp',
            'alicloud_security_group_rule.allow_all_telnet',
            'alicloud_security_group_rule.allow_all_vnclistener',
            'alicloud_security_group_rule.allow_all_vncserver',
        }
        failing_resources = {
            'alicloud_security_group_rule.allow_all_tcp',
            'alicloud_security_group_rule.allow_all_tcp2',
            'alicloud_security_group_rule.allow_all_low',
            'alicloud_security_group_rule.allow_all_ssh',
        }
        skipped_resources = {}

        passed_check_resources = set([c.resource for c in report.passed_checks])
        failed_check_resources = set([c.resource for c in report.failed_checks])

        self.assertEqual(summary['passed'], len(passing_resources))
        self.assertEqual(summary['failed'], len(failing_resources))
        self.assertEqual(summary['skipped'], len(skipped_resources))
        self.assertEqual(summary['parsing_errors'], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == '__main__':
    unittest.main()