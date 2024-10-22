#pass
resource "aws_sfn_state_machine" "XrayEnabled" {
  name     = "XrayEnabled"
  role_arn = "example"

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
      tracing_configuration {
        enabled = true
      }
    }

#fail

resource "aws_sfn_state_machine" "XrayDisabled" {
  name     = "XrayDisabled"
  role_arn = "EOF.iam_for_sfn.arn"

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
      tracing_configuration {
        enabled = false
      }
    }

resource "aws_sfn_state_machine" "XrayDefault" {
  name     = "XrayDisabled"
  role_arn = "EOF.iam_for_sfn.arn"

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