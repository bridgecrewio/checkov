import unittest

from checkov.terraformscanner.models.enums import ScanResult
from checkov.terraformscanner.resource_scanners.aws.SecurityGroupUnrestrictedIngress22 import scanner


class TestSecurityGroupUnrestrictedIngress22(unittest.TestCase):

    def test_failure(self):
        resource_conf = {'name': ['foo'],
                         'vpc_id': ['${var.vpc_id}'], 'ingress': [
                {'from_port': [22], 'to_port': [22], 'protocol': ['TCP'], 'cidr_blocks': [['0.0.0.0/0']]},
                {'from_port': [443], 'to_port': [443], 'protocol': ['TCP'], 'cidr_blocks': [['0.0.0.0/0']]}],
                         'egress': [
                             {'from_port': [0], 'to_port': [0], 'protocol': ['-1'], 'cidr_blocks': [['0.0.0.0/0']]}]
                        }

        scan_result = scanner.scan_resource_conf(conf=resource_conf)
        self.assertEqual(ScanResult.FAILURE, scan_result)

    def test_success(self):
        resource_conf =  {'name': ['foo'],
                          'vpc_id': ['${var.vpc_id}'], 'ingress': [
                {'from_port': [80], 'to_port': [80], 'protocol': ['TCP'], 'cidr_blocks': [['0.0.0.0/0']]},
                {'from_port': [443], 'to_port': [443], 'protocol': ['TCP'], 'cidr_blocks': [['0.0.0.0/0']]}],
                          'egress': [
                              {'from_port': [0], 'to_port': [0], 'protocol': ['-1'], 'cidr_blocks': [['0.0.0.0/0']]}],
                          'tags': [{'kubernetes.io/cluster/${var.cluster_name}': 'owned',
                                    'kubernetes:application': '${local.name}'}]}
        scan_result = scanner.scan_resource_conf(conf=resource_conf)
        self.assertEqual(ScanResult.SUCCESS, scan_result)


if __name__ == '__main__':
    unittest.main()
