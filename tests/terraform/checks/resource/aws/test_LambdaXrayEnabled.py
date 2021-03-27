import unittest

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.aws.LambdaXrayEnabled import check


class TestLambdaXrayEnabled(unittest.TestCase):
    def test_failure(self):
        resource_conf = {
            "description": "${var.description}",
            "environment": [{"variables": "${var.envvar}"}],
            "filename": "${var.filename}",
            "function_name": "${var.name}",
            "handler": "${var.handler}",
            "layers": "${var.layers}",
            "lifecycle": [{"ignore_changes": ["last_modified", "tags"]}],
            "memory_size": "${var.memory_size}",
            "role": "${var.role_arn}",
            "runtime": "${var.runtime}",
            "s3_bucket": "${var.s3_bucket}",
            "s3_key": "${var.s3_key}",
            "tags": "${var.common_tags}",
            "timeout": "${var.timeout}",
            "vpc_config": [
                {
                    "security_group_ids": "${var.security_group_ids}",
                    "subnet_ids": "${var.subnet_ids}",
                }
            ],
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource_conf = {
            "description": "${var.description}",
            "environment": [{"variables": "${var.envvar}"}],
            "filename": "${var.filename}",
            "function_name": "${var.name}",
            "handler": "${var.handler}",
            "layers": "${var.layers}",
            "lifecycle": [{"ignore_changes": ["last_modified", "tags"]}],
            "memory_size": "${var.memory_size}",
            "role": "${var.role_arn}",
            "runtime": "${var.runtime}",
            "s3_bucket": "${var.s3_bucket}",
            "s3_key": "${var.s3_key}",
            "tags": "${var.common_tags}",
            "timeout": "${var.timeout}",
            "tracing_config": [{"mode": "PassThrough"}],
            "vpc_config": [
                {
                    "security_group_ids": "${var.security_group_ids}",
                    "subnet_ids": "${var.subnet_ids}",
                }
            ],
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == "__main__":
    unittest.main()
