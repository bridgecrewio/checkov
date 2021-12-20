# pass

resource "aws_appsync_graphql_api" "enabled" {
  authentication_type = "API_KEY"
  name                = "example"

  log_config {
    cloudwatch_logs_role_arn = "aws_iam_role.example.arn"
    field_log_level          = "ERROR"
  }
}

# fail

resource "aws_appsync_graphql_api" "default" {
  authentication_type = "API_KEY"
  name                = "example"
}
