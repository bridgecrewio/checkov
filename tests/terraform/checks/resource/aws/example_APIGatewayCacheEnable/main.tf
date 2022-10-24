resource "aws_api_gateway_stage" "pass" {
  name                  = "example"
  cache_cluster_enabled = true
}

resource "aws_api_gateway_stage" "fail" {
  name = "example"
}


