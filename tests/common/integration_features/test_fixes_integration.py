from __future__ import annotations

import os
import unittest
from typing import Any, Iterable

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.bridgecrew.integration_features.features.fixes_integration import FixesIntegration
from checkov.common.bridgecrew.integration_features.features.policy_metadata_integration import integration as metadata_integration
from checkov.common.bridgecrew.platform_integration import BcPlatformIntegration
from checkov.common.models.enums import CheckResult
from checkov.common.output.record import Record
from checkov.common.output.report import Report


_old_check_metadata = None


class TestFixesIntegration(unittest.TestCase):
    def test_integration_valid(self):
        instance = BcPlatformIntegration()
        instance.skip_fixes = False
        instance.platform_integration_configured = True
        instance.on_prem = False

        fixes_integration = FixesIntegration(instance)

        self.assertTrue(fixes_integration.is_valid())

        instance.on_prem = True
        self.assertFalse(fixes_integration.is_valid())

        instance.on_prem = False
        instance.skip_fixes = True
        self.assertFalse(fixes_integration.is_valid())

        instance.platform_integration_configured = False
        self.assertFalse(fixes_integration.is_valid())

        instance.skip_fixes = False
        self.assertFalse(fixes_integration.is_valid())

        fixes_integration.integration_feature_failures = True
        self.assertFalse(fixes_integration.is_valid())

    def test_apply_fixes_to_report(self):
        instance = BcPlatformIntegration()
        instance.skip_fixes = False
        instance.platform_integration_configured = True

        fixes_integration = FixesIntegration(instance)
        fixes_integration._get_fixes_for_file = mock_fixes_response

        metadata_integration.check_metadata = {
            'custom_aws_12345': {'guideline': 'https://docs.bridgecrew.io/docs/ensure-vpc-subnets-do-not-assign-public-ip-by-default'},
            'CKV_AWS_130': {
                'id': 'BC_AWS_NETWORKING_53',
                'title': 'Ensure VPC subnets do not assign public IP by default',
                'guideline': 'https://docs.bridgecrew.io/docs/ensure-vpc-subnets-do-not-assign-public-ip-by-default',
                'severity': 'MEDIUM',
                'pcSeverity': 'MEDIUM',
                'category': 'Networking',
                'checkovId': 'CKV_AWS_130',
                'constructiveTitle': 'Ensure VPC subnets do not assign public IP by default',
                'descriptiveTitle': 'AWS VPC subnets should not allow automatic public IP assignment',
                'pcPolicyId': '11743cd3-35e4-4639-91e1-bc87b52d4cf5',
                'additionalPcPolicyIds': ['11743cd3-35e4-4639-91e1-bc87b52d4cf5'],
                'benchmarks': {}
            }
        }

        metadata_integration.bc_to_ckv_id_mapping = {
            'BC_AWS_NETWORKING_53': 'CKV_AWS_130'
        }

        report = Report(CheckType.TERRAFORM)

        file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources', 'main.tf')

        report.add_record(Record(
            check_id='CKV_AWS_130',
            bc_check_id='BC_AWS_NETWORKING_53',
            check_result={'result': CheckResult.FAILED, 'evaluated_keys': ['map_public_ip_on_launch']},
            check_name='Ensure VPC subnets do not assign public IP by default',
            check_class='checkov.terraform.checks.resource.aws.SubnetPublicIP',
            code_block=[(1, 'resource "aws_subnet" "s" {\n'), (2, '  map_public_ip_on_launch = true\n'), (3, '}\n')],
            evaluations=None,
            file_abs_path=file,
            file_line_range=[2, 3],
            file_path='/main.tf',
            resource='aws_subnet.s'
        ))

        report.add_record(Record(
            check_id='custom_aws_12345',
            bc_check_id='custom_aws_12345',
            check_result={'result': CheckResult.FAILED, 'evaluated_keys': ['map_public_ip_on_launch']},
            check_name='Cloned-Ensure VPC subnets do not assign public IP by default',
            check_class='checkov.terraform.checks.resource.aws.SubnetPublicIP',
            code_block=[(1, 'resource "aws_subnet" "s" {\n'), (2, '  map_public_ip_on_launch = true\n'), (3, '}\n')],
            evaluations=None,
            file_abs_path=file,
            file_line_range=[2, 3],
            file_path='/main.tf',
            resource='aws_subnet.s'
        ))

        fixes_integration.post_runner(report)

        self.assertTrue(all(r.fixed_definition is not None for r in report.failed_checks))

    def setUp(self) -> None:
        self._old_check_metadata = metadata_integration.check_metadata

    def tearDown(self) -> None:
        metadata_integration.check_metadata = self._old_check_metadata
        metadata_integration.bc_to_ckv_id_mapping = {}


def mock_fixes_response(check_type: str, filename: str, file_contents: str, failed_checks: Iterable[Record]
    ) -> dict[str, Any] | None:
    return {
        'filePath': '/private/tmp/custom/main.tf',
        'fixes': [
            {
                'resourceId': 'aws_subnet.s',
                'policyId': 'BC_AWS_NETWORKING_53',
                'originalStartLine': 1,
                'originalEndLine': 3,
                'fixedDefinition': 'resource "aws_subnet" "s" {\n}\n'
            },
            {
                'resourceId': 'aws_subnet.s',
                'policyId': 'custom_aws_12345',
                'originalStartLine': 1,
                'originalEndLine': 3,
                'fixedDefinition': 'resource "aws_subnet" "s" {\n}\n'
            }
        ]
    }


if __name__ == '__main__':
    unittest.main()
