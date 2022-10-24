import unittest

import hcl2

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.openstack.SecurityGroupUnrestrictedIngress22 import check


class TestSecurityGroupUnrestrictedIngress22(unittest.TestCase):

    def test_failure_compute_secgroup_ipv4(self):
        hcl_res = hcl2.loads("""
        resource "openstack_compute_secgroup_v2" "secgroup_1" {
          name        = "my_secgroup"
          description = "my security group"

          rule {
            from_port   = 80
            to_port     = 80
            ip_protocol = "tcp"
            cidr        = "0.0.0.0/0"
          }

          rule {
            from_port   = 22
            to_port     = 22
            ip_protocol = "tcp"
            cidr        = "192.168.0.0/16"
          }

          rule {
            from_port   = 22
            to_port     = 22
            ip_protocol = "tcp"
            cidr        = "0.0.0.0/0"
          }
        }
        """)
        resource_conf = hcl_res['resource'][0]['openstack_compute_secgroup_v2']['secgroup_1']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_compute_secgroup_port_range(self):
        hcl_res = hcl2.loads("""
        resource "openstack_compute_secgroup_v2" "secgroup_1" {
          name        = "my_secgroup"
          description = "my security group"
        
          rule {
            from_port   = 0
            to_port     = 65535
            ip_protocol = "tcp"
            cidr        = "0.0.0.0/0"
          }
        }
        """)
        resource_conf = hcl_res['resource'][0]['openstack_compute_secgroup_v2']['secgroup_1']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_compute_secgroup_ipv6(self):
        hcl_res = hcl2.loads("""
        resource "openstack_compute_secgroup_v2" "secgroup_1" {
          name        = "my_secgroup"
          description = "my security group"
        
          rule {
            from_port   = 22
            to_port     = 22
            ip_protocol = "tcp"
            cidr        = "192.168.0.0/16"
          }
          rule {
            from_port   = 22
            to_port     = 22
            ip_protocol = "tcp"
            cidr        = "::/0"
          }
        }
        """)
        resource_conf = hcl_res['resource'][0]['openstack_compute_secgroup_v2']['secgroup_1']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_pass_compute_secgroup_different_port(self):
        hcl_res = hcl2.loads("""
        resource "openstack_compute_secgroup_v2" "secgroup_1" {
          name        = "my_secgroup"
          description = "my security group"

          rule {
            from_port   = 222
            to_port     = 222
            ip_protocol = "tcp"
            cidr        = "192.168.0.0/16"
          }

          rule {
            from_port   = 222
            to_port     = 222
            ip_protocol = "tcp"
            cidr        = "0.0.0.0/0"
          }
        }
        """)
        resource_conf = hcl_res['resource'][0]['openstack_compute_secgroup_v2']['secgroup_1']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_pass_compute_secgroup_no_cidr(self):
        hcl_res = hcl2.loads("""
        resource "openstack_compute_secgroup_v2" "secgroup_1" {
          name        = "my_secgroup"
          description = "my security group"
        
          rule {
            from_port     = 22
            to_port       = 22
            ip_protocol   = "tcp"
            from_group_id = "5338c192-5118-11ec-bf63-0242ac130002"
          }
        }
        """)
        resource_conf = hcl_res['resource'][0]['openstack_compute_secgroup_v2']['secgroup_1']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_pass_compute_secgroup_null_cidr(self):
        hcl_res = hcl2.loads("""
        resource "openstack_compute_secgroup_v2" "secgroup_1" {
          name        = "my_secgroup"
          description = "my security group"
        
          rule {
            from_port   = 22
            to_port     = 22
            ip_protocol = "tcp"
            cidr        = null
          }
        }
            """)
        resource_conf = hcl_res['resource'][0]['openstack_compute_secgroup_v2']['secgroup_1']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_pass_compute_secgroup_cidr(self):
        hcl_res = hcl2.loads("""
        resource "openstack_compute_secgroup_v2" "secgroup_1" {
          name        = "my_secgroup"
          description = "my security group"
        
          rule {
            from_port   = 22
            to_port     = 22
            ip_protocol = "tcp"
            cidr        = "192.168.0.0/16"
          }
        }
        """)
        resource_conf = hcl_res['resource'][0]['openstack_compute_secgroup_v2']['secgroup_1']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_pass_compute_secgroup_icmp(self):
        hcl_res = hcl2.loads("""
        resource "openstack_compute_secgroup_v2" "secgroup_1" {
          name        = "my_secgroup"
          description = "my security group"
        
          rule {
            from_port   = 22
            to_port     = 22
            ip_protocol = "icmp"
            cidr        = "0.0.0.0/0"
          }
        }
        """)

        resource_conf = hcl_res['resource'][0]['openstack_compute_secgroup_v2']['secgroup_1']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


    def test_failure_networking_secgroup(self):
        hcl_res = hcl2.loads("""
        resource "openstack_networking_secgroup_v2" "secgroup_1" {
          name        = "secgroup_1"
          description = "My neutron security group"
        }
        
        resource "openstack_networking_secgroup_rule_v2" "ingress" {
          direction         = "ingress"
          ethertype         = "IPv4"
          protocol          = "tcp"
          port_range_min    = 22
          port_range_max    = 22
          remote_ip_prefix  = "0.0.0.0/0"
        }
        """)

        resource_conf = hcl_res['resource'][0]['openstack_networking_secgroup_v2']['secgroup_1']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

        resource_conf = hcl_res['resource'][1]['openstack_networking_secgroup_rule_v2']['ingress']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_networking_secgroup_port_range(self):
        hcl_res = hcl2.loads("""
        resource "openstack_networking_secgroup_rule_v2" "ingress" {
          direction         = "ingress"
          ethertype         = "IPv4"
          protocol          = "tcp"
          port_range_min    = 1
          port_range_max    = 65535
          remote_ip_prefix  = "0.0.0.0/0"
        }
        """)

        resource_conf = hcl_res['resource'][0]['openstack_networking_secgroup_rule_v2']['ingress']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_pass_networking_secgroup(self):
        hcl_res = hcl2.loads("""
        resource "openstack_networking_secgroup_rule_v2" "ingress" {
          direction         = "ingress"
          ethertype         = "IPv4"
          protocol          = "tcp"
          port_range_min    = 22
          port_range_max    = 22
          remote_ip_prefix  = "192.168.0.0/16"
          security_group_id = "${openstack_networking_secgroup_v2.secgroup_1.id}"
        }
        """)

        resource_conf = hcl_res['resource'][0]['openstack_networking_secgroup_rule_v2']['ingress']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_pass_networking_secgroup_icmp(self):
        hcl_res = hcl2.loads("""
        resource "openstack_networking_secgroup_rule_v2" "ingress" {
          direction         = "ingress"
          ethertype         = "IPv4"
          protocol          = "icmp"
          port_range_min    = 22
          port_range_max    = 22
          remote_ip_prefix  = "0.0.0.0/0"
        }
        """)

        resource_conf = hcl_res['resource'][0]['openstack_networking_secgroup_rule_v2']['ingress']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_unknown_networking_secgroup_egress(self):
        hcl_res = hcl2.loads("""
        resource "openstack_networking_secgroup_rule_v2" "egress" {
          direction         = "egress"
          ethertype         = "IPv4"
          protocol          = "tcp"
          port_range_min    = 22
          port_range_max    = 22
          remote_ip_prefix  = "0.0.0.0/0"
        }
        """)

        resource_conf = hcl_res['resource'][0]['openstack_networking_secgroup_rule_v2']['egress']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.UNKNOWN, scan_result)

    def test_pass_networking_secgroup_source_sg(self):
        hcl_res = hcl2.loads("""
        resource "openstack_networking_secgroup_rule_v2" "ingress" {
          direction         = "ingress"
          ethertype         = "IPv4"
          protocol          = "tcp"
          port_range_min    = 22
          port_range_max    = 22
          security_group_id = "${openstack_networking_secgroup_v2.secgroup_1.id}"
        }
        """)

        resource_conf = hcl_res['resource'][0]['openstack_networking_secgroup_rule_v2']['ingress']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_pass_networking_secgroup_different_port(self):
        hcl_res = hcl2.loads("""
        resource "openstack_networking_secgroup_rule_v2" "ingress" {
          direction         = "ingress"
          ethertype         = "IPv4"
          protocol          = "tcp"
          port_range_min    = 222
          port_range_max    = 222
          remote_ip_prefix  = "0.0.0.0/0"
        }
        """)

        resource_conf = hcl_res['resource'][0]['openstack_networking_secgroup_rule_v2']['ingress']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
