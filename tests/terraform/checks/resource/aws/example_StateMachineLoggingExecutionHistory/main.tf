#pass
resource "aws_sfn_state_machine" "StateMachineLoggingExecutionHistoryEnabled" {
  name     = "my-state-machine"
  role_arn = "example1"

  definition = <<EOF
{
  "StartAt": "HelloWorld",
  "States": {
    "HelloWorld": {
      "Type": "Task",
      "Resource": "${aws_lambda_function.lambda.arn}",
      "End": true
    }
  }
}
EOF

  logging_configuration {
    log_destination        = "${aws_cloudwatch_log_group.log_group_for_sfn.arn}:*"
    include_execution_data = true
    level                  = "ERROR"
  }
}

#fail

resource "aws_sfn_state_machine" "StateMachineLoggingExecutionHistoryDisabled" {
  name     = "my-state-machine"
  role_arn = "example2"

  definition = <<EOF
{
  "StartAt": "HelloWorld",
  "States": {
    "HelloWorld": {
      "Type": "Task",
      "Resource": "${aws_lambda_function.lambda.arn}",
      "End": true
    }
  }
}
EOF

  logging_configuration {
    log_destination        = "${aws_cloudwatch_log_group.log_group_for_sfn.arn}:*"
    include_execution_data = false
    level                  = "ERROR"
  }
}


resource "aws_sfn_state_machine" "StateMachineLoggingExecutionHistoryDefault" {
  name     = "my-state-machine"
  role_arn = "example3"

  definition = <<EOF
{
  "StartAt": "HelloWorld",
  "States": {
    "HelloWorld": {
      "Type": "Task",
      "Resource": "${aws_lambda_function.lambda.arn}",
      "End": true
    }
  }
}
EOF


}
