resource "aws_sagemaker_endpoint_configuration" "production_variants_pass_1" {
                name = "my-endpoint-config"
                production_variants {
                    variant_name           = "variant-1"
                    model_name             = aws_sagemaker_model.model.name
                    initial_instance_count = 1
                    instance_type          = "ml.t2.medium"
                }
            }

resource "aws_sagemaker_endpoint_configuration" "production_variants_pass_2" {
                name = "my-endpoint-config"
                production_variants {
                    variant_name           = "variant-1"
                    model_name             = aws_sagemaker_model.model1.name
                    initial_instance_count = 1
                    instance_type          = "ml.t2.medium"
                }
                production_variants {
                    variant_name           = "variant-2"
                    model_name             = aws_sagemaker_model.model2.name
                    initial_instance_count = 2
                    instance_type          = "ml.m5.large"
                }
            }

resource "aws_sagemaker_endpoint_configuration" "production_variants_fail" {
                name = "my-endpoint-config"
            }