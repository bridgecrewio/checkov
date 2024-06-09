resource "aws_sagemaker_flow_definition" "flow_pass" {
  flow_definition_name = "example"
  role_arn             = aws_iam_role.example.arn

  human_loop_config {
    human_task_ui_arn                     = aws_sagemaker_human_task_ui.example.arn
    task_availability_lifetime_in_seconds = 1
    task_count                            = 1
    task_description                      = "example"
    task_title                            = "example"
    workteam_arn                          = aws_sagemaker_workteam.example.arn
  }

  output_config {
    kms_key_id = "abc"
    s3_output_path = "s3://${aws_s3_bucket.example.bucket}/"
  }
}

resource "aws_sagemaker_flow_definition" "flow_fail" {
  flow_definition_name = "example"
  role_arn             = aws_iam_role.example.arn

  human_loop_config {
    human_task_ui_arn                     = aws_sagemaker_human_task_ui.example.arn
    task_availability_lifetime_in_seconds = 1
    task_count                            = 1
    task_description                      = "example"
    task_title                            = "example"
    workteam_arn                          = aws_sagemaker_workteam.example.arn
  }

  output_config {
    s3_output_path = "s3://${aws_s3_bucket.example.bucket}/"
  }
}