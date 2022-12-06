resource "aws_config_configuration_recorder" "pass_recorder" {
  name     = "example"
  role_arn = aws_iam_role.r.arn

  recording_group {
    include_global_resource_types = true
  }
  
}

resource "aws_config_configuration_recorder_status" "pass" {
  name       = aws_config_configuration_recorder.pass_recorder.name
  is_enabled = true
}

resource "aws_config_configuration_recorder" "fail_recorder_1" {
  name     = "example"
  role_arn = aws_iam_role.r.arn
  
}

resource "aws_config_configuration_recorder_status" "fail_1" {
  name       = aws_config_configuration_recorder.fail_recorder_1.name
  is_enabled = false
}

resource "aws_config_configuration_recorder" "fail_recorder_2" {
  name     = "example"
  role_arn = aws_iam_role.r.arn
  recording_group {
    all_supported = false
  }
}

resource "aws_config_configuration_recorder_status" "fail_2" {
  name       = aws_config_configuration_recorder.fail_recorder_2.name
  is_enabled = true
}