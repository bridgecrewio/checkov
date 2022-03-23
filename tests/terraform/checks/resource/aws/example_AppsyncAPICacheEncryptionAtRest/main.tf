resource "aws_appsync_api_cache" "pass" {
  api_id                     = aws_appsync_graphql_api.default.id
  transit_encryption_enabled = true
  at_rest_encryption_enabled = true
  ttl                        = 60
  type                       = "SMALL"
  api_caching_behavior       = "FULL_REQUEST_CACHING"
}

resource "aws_appsync_api_cache" "fail" {
  api_id                     = aws_appsync_graphql_api.default.id
  transit_encryption_enabled = false
  at_rest_encryption_enabled = false
  ttl                        = 60
  type                       = "SMALL"
  api_caching_behavior       = "FULL_REQUEST_CACHING"
}

resource "aws_appsync_api_cache" "fail2" {
  api_id               = aws_appsync_graphql_api.default.id
  ttl                  = 60
  type                 = "SMALL"
  api_caching_behavior = "FULL_REQUEST_CACHING"
}
