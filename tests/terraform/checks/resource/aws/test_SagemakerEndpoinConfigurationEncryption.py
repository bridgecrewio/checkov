import unittest
import hcl2

from checkov.terraform.checks.resource.aws.SagemakerEndpointConfigurationEncryption import check
from checkov.common.models.enums import CheckResult


class TestSagemakerEndpointConfigurationEncryption(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
                resource "aws_sagemaker_endpoint_configuration" "test" {
                    name = "my-endpoint-config"

                    production_variants {
                      variant_name           = "variant-1"
                      model_name             = aws_sagemaker_model.m.name
                      initial_instance_count = 1
                      instance_type          = "ml.t2.medium"
                    }
                }
        """)
        resource_conf = hcl_res['resource'][0]['aws_sagemaker_endpoint_configuration']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
                resource "aws_sagemaker_endpoint_configuration" "test" {
                    name = "my-endpoint-config"
                    kms_key_arn = aws_kms_key.test.arn
                    
                    production_variants {
                      variant_name           = "variant-1"
                      model_name             = aws_sagemaker_model.m.name
                      initial_instance_count = 1
                      instance_type          = "ml.t2.medium"
                    }
                }
        """)
        resource_conf = hcl_res['resource'][0]['aws_sagemaker_endpoint_configuration']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

if __name__ == '__main__':
    unittest.main()
