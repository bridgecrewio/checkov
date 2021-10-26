resource "aws_sagemaker_notebook_instance" "pass" {
  name          = "examplea"
  role_arn      = aws_iam_role.test.arn
  instance_type = "ml.t2.medium"
  kms_key_id    = aws_kms_key.test.id
}

resource "aws_sagemaker_notebook_instance" "fail" {
  name          = "examplea"
  role_arn      = aws_iam_role.test.arn
  instance_type = "ml.t2.medium"
}
