import unittest

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.aws.ECRPolicy import check


class TestECRPolicy(unittest.TestCase):
    def test_failure(self):
        resource_conf = {
            "repository": ["public_repo"],
            "policy": [
                '{\n    "Version": "2008-10-17",\n    "Statement": [\n        {\n            "Sid": "new policy",'
                '\n            "Effect": "Allow",\n            "Principal": "*",\n            "Action": [\n               '
                ' "ecr:GetDownloadUrlForLayer",\n                "ecr:BatchGetImage",\n                '
                '"ecr:BatchCheckLayerAvailability",\n                "ecr:PutImage",\n                '
                '"ecr:InitiateLayerUpload",\n                "ecr:UploadLayerPart",\n                '
                '"ecr:CompleteLayerUpload",\n                "ecr:DescribeRepositories",\n                '
                '"ecr:GetRepositoryPolicy",\n                "ecr:ListImages",\n                "ecr:DeleteRepository",'
                '\n                "ecr:BatchDeleteImage",\n                "ecr:SetRepositoryPolicy",\n                '
                '"ecr:DeleteRepositoryPolicy"\n            ]\n        }\n    ]\n}'
            ],
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource_conf = {
            "repository": ["private_repo"],
            "policy": [
                '{\n    "Version": "2008-10-17",\n    "Statement": [\n        {\n            "Sid": "new policy",'
                '\n            "Effect": "Allow",\n            "Principal": {\n                "AWS": [\n                 '
                '   "arn:aws:iam::123456789012:user/pull-user-1",\n                    '
                '"arn:aws:iam::123456789012:user/pull-user-2"\n                ]\n            },\n            "Action": ['
                '\n                "ecr:GetDownloadUrlForLayer",\n                "ecr:BatchGetImage",\n                '
                '"ecr:BatchCheckLayerAvailability",\n                "ecr:PutImage",\n                '
                '"ecr:InitiateLayerUpload",\n                "ecr:UploadLayerPart",\n                '
                '"ecr:CompleteLayerUpload",\n                "ecr:DescribeRepositories",\n                '
                '"ecr:GetRepositoryPolicy",\n                "ecr:ListImages",\n                "ecr:DeleteRepository",'
                '\n                "ecr:BatchDeleteImage",\n                "ecr:SetRepositoryPolicy",\n                '
                '"ecr:DeleteRepositoryPolicy"\n            ]\n        }\n    ]\n}'
            ],
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == "__main__":
    unittest.main()
