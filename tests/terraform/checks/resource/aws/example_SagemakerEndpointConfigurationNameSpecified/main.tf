resource "aws_sagemaker_endpoint_configuration" "name_fail" {
  kms_key_arn = aws_kms_key.test.arn
  production_variants {
    variant_name           = "variant-1"
    model_name             = aws_sagemaker_model.m.name
    initial_instance_count = 1
    instance_type          = "ml.t2.medium"
  }
  tags = {
    Name = "foo"
  }
}

resource "aws_sagemaker_endpoint_configuration" "name_pass" {
  name = "my-endpoint-config"
  kms_key_arn = aws_kms_key.test.arn
  production_variants {
    variant_name           = "variant-1"
    model_name             = aws_sagemaker_model.m.name
    initial_instance_count = 1
    instance_type          = "ml.t2.medium"
  }
  tags = {
    Name = "foo"
  }
}


