resource "aws_sagemaker_image_version" "test" {
  image_name = "name"
  base_image = "012345678912.dkr.ecr.us-west-2.amazonaws.com/image:latest"
}