resource "aws_api_gateway_rest_api" "fail" {
  name = "example"
  tags = { test = "Fail" }
  # lifecycle {
  #   create_before_destroy=true
  # }
}

resource "aws_api_gateway_rest_api" "fail2" {
  name = "example"
  tags = { test = "Fail" }
  lifecycle {
    create_before_destroy = false
  }
}

resource "aws_api_gateway_rest_api" "pass" {
  name = "example"
  tags = { test = "Fail" }
  lifecycle {
    create_before_destroy = true
  }
}