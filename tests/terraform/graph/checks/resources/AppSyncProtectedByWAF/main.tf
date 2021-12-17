# pass

resource "aws_appsync_graphql_api" "pass" {
  authentication_type = "API_KEY"
  name                = "example"
}

resource "aws_wafv2_web_acl_association" "pass" {
  resource_arn = aws_appsync_graphql_api.pass.arn
  web_acl_arn  = aws_wafv2_web_acl.example.arn
}

# fail

resource "aws_appsync_graphql_api" "fail" {
  authentication_type = "API_KEY"
  name                = "example"
}
