resource "aws_api_gateway_deployment" "pass" {
  rest_api_id = "some rest api id"
  stage_name  = "some name"
  lifecycle {
    create_before_destroy = true
  }
  tags {
    project = "ProjectName"
  }
}


resource "aws_api_gateway_deployment" "fail" {
  rest_api_id = "some rest api id"
  stage_name  = "some name"
  lifecycle {
    create_before_destroy = false
  }
  tags {
    project = "ProjectName"
  }
}

resource "aws_api_gateway_deployment" "fail2" {
  rest_api_id = "some rest api id"
  stage_name  = "some name"

  tags {
    project = "ProjectName"
  }
}
