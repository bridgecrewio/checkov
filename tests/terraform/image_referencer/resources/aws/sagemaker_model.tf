resource "aws_sagemaker_model" "example1" {
  name               = "my-model"
  execution_role_arn = "arn:aws:iam::123456789012:role/SageMakerExecutionRole"

  primary_container {
    image = "012345678912.dkr.ecr.us-west-2.amazonaws.com/image1:latest"
  }
}

resource "aws_sagemaker_model" "example2" {
  name               = "my-model"
  execution_role_arn = "arn:aws:iam::123456789012:role/SageMakerExecutionRole"

  container {
    image = "012345678912.dkr.ecr.us-west-2.amazonaws.com/image2:latest"
  }
}
