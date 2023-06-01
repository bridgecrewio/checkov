import hcl2
import unittest

from checkov.terraform.checks.resource.aws.MQBrokerNotPubliclyExposed import check
from checkov.common.models.enums import CheckResult


class TestMQBrokerNotPubliclyExposed(unittest.TestCase):

    def test_failure_mqbroker_logging(self):
        hcl_res = hcl2.loads("""
        resource "aws_mq_broker" "example" {
            broker_name = "example"

            engine_type         = "ActiveMQ"
            engine_version      = "5.15.0"
            host_instance_type  = "mq.t2.micro"
            publicly_accessible = true

            user {
                username = "ExampleUser"
                password = "MindTheGap"  # checkov:skip=CKV_SECRET_6 test secret
            }
        }
        """)
        resource_conf = hcl_res['resource'][0]['aws_mq_broker']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success_mqbroker_logging(self):
        hcl_res = hcl2.loads("""
        resource "aws_mq_broker" "example" {
            broker_name = "example"

            engine_type         = "ActiveMQ"
            engine_version      = "5.15.0"
            host_instance_type  = "mq.t2.micro"
            publicly_accessible = false

            user {
                username = "ExampleUser"
                password = "MindTheGap"
            }
        }
        """)
        resource_conf = hcl_res['resource'][0]['aws_mq_broker']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_missing_mqbroker_logging(self):
        hcl_res = hcl2.loads("""
        resource "aws_mq_broker" "example" {
            broker_name = "example"

            engine_type         = "ActiveMQ"
            engine_version      = "5.15.0"
            host_instance_type  = "mq.t2.micro"

            user {
                username = "ExampleUser"
                password = "MindTheGap"
            }
        }
        """)
        resource_conf = hcl_res['resource'][0]['aws_mq_broker']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
