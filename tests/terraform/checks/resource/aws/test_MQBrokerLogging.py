import unittest

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.aws.MQBrokerLogging import check


class TestMQBrokerLogging(unittest.TestCase):
    def test_failure_mqbroker_logging(self):
        resource_conf = {
            "broker_name": "example",
            "configuration": [
                {
                    "id": "${aws_mq_configuration.test.id}",
                    "revision": "${aws_mq_configuration.test.latest_revision}",
                }
            ],
            "engine_type": "ActiveMQ",
            "engine_version": "5.15.0",
            "host_instance_type": "mq.t2.micro",
            "security_groups": ["${aws_security_group.test.id}"],
            "user": [{"password": "MindTheGap", "username": "ExampleUser"}],
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success_mqbroker_logging(self):

        resource_conf = {
            "broker_name": "example",
            "configuration": [
                {
                    "id": "${aws_mq_configuration.test.id}",
                    "revision": "${aws_mq_configuration.test.latest_revision}",
                }
            ],
            "engine_type": "ActiveMQ",
            "engine_version": "5.15.0",
            "host_instance_type": "mq.t2.micro",
            "security_groups": ["${aws_security_group.test.id}"],
            "user": [{"password": "MindTheGap", "username": "ExampleUser"}],
            "logs": [{"general": [True]}],
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == "__main__":
    unittest.main()
