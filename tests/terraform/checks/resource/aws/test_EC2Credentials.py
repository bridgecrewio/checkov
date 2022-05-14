import unittest

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.aws.EC2Credentials import check


class TestEC2Credentials(unittest.TestCase):
    def test_success(self):
        conf = {
            "ami": ["ami-04169656fea786776"],
            "instance_type": ["t2.nano"],
            "user_data": [
                '#! /bin/bash\nsudo apt-get update\nsudo apt-get install -y apache2\nsudo systemctl start apache2\nsudo systemctl enable apache2\nexport AWS_ACCESS_KEY_ID\nexport AWS_ACCESS_KEY_ID=FOO\nexport AWS_SECRET_ACCESS_KEY=bar\nexport AWS_DEFAULT_REGION=us-west-2\necho "<h1>Deployed via Terraform</h1>" | sudo tee /var/www/html/index.html'
            ],
            "tags": [{"Name": "${local.resource_prefix.value}-ec2"}],
        }

        scan_result = check.scan_resource_conf(conf=conf)
        self.assertEqual(CheckResult.PASSED, scan_result)
        conf = {"ami": ["ami-04169656fea786776"], "instance_type": ["t2.nano"]}
        scan_result = check.scan_resource_conf(conf=conf)

        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_failure(self):
        conf = {
            "ami": ["ami-04169656fea786776"],
            "instance_type": ["t2.nano"],
            "user_data": [
                '#! /bin/bash\nsudo apt-get update\nsudo apt-get install -y apache2\nsudo systemctl start apache2\nsudo systemctl enable apache2\nexport AWS_ACCESS_KEY_ID\nexport AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE\nexport AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY\nexport AWS_DEFAULT_REGION=us-west-2\necho "<h1>Deployed via Terraform</h1>" | sudo tee /var/www/html/index.html'
            ],
            "tags": [{"Name": "${local.resource_prefix.value}-ec2"}],
        }
        scan_result = check.scan_resource_conf(conf=conf)
        self.assertEqual(CheckResult.FAILED, scan_result)


if __name__ == "__main__":
    unittest.main()
