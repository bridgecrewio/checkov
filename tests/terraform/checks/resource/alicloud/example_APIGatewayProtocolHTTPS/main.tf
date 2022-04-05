resource "alicloud_api_gateway_api" "fail" {
  name              = alicloud_api_gateway_group.apiGroup.name
  group_id          = alicloud_api_gateway_group.apiGroup.id
  description       = "your description"
  auth_type         = "APP"
  force_nonce_check = false

  request_config {
    protocol = "HTTP" #this should HTTPS
    method   = "GET"
    path     = "/test/path1"
    mode     = "MAPPING"
  }

   service_type = "HTTP"

  http_service_config {
    address   = "http://apigateway-backend.alicloudapi.com:8080"
    method    = "GET"
    path      = "/web/cloudapi"
    timeout   = 12
    aone_name = "cloudapi-openapi"
  }
}

resource "alicloud_api_gateway_api" "fail2" {
  name              = alicloud_api_gateway_group.apiGroup.name
  group_id          = alicloud_api_gateway_group.apiGroup.id
  description       = "your description"
  auth_type         = "APP"
  force_nonce_check = false

  request_config {
    protocol = "HTTP" #this should HTTPS
    method   = "GET"
    path     = "/test/path1"
    mode     = "MAPPING"
  }

  service_type = "HTTP"

  http_service_config {
    address   = "http://apigateway-backend.alicloudapi.com:8080"
    method    = "GET"
    path      = "/web/cloudapi"
    timeout   = 12
    aone_name = "cloudapi-openapi"
  }

  request_parameters {
    name         = "aaa"
    type         = "STRING"
    required     = "OPTIONAL"
    in           = "QUERY"
    in_service   = "QUERY"
    name_service = "testparams"
  }

  stage_names = [
    "RELEASE",
    "TEST",
  ]
}


resource "alicloud_api_gateway_api" "fail3" {
  name              = alicloud_api_gateway_group.apiGroup.name
  group_id          = alicloud_api_gateway_group.apiGroup.id
  description       = "your description"
  auth_type         = "APP"
  force_nonce_check = false

  request_config {
    protocol = "HTTP"
    method   = "GET"
    path     = "/test/path1"
    mode     = "MAPPING"
  }

  request_config {
    protocol = "HTTP"
    method   = "GET"
    path     = "/test/path2"
    mode     = "MAPPING"
  }

  service_type = "HTTP"

  http_service_config {
    address   = "http://apigateway-backend.alicloudapi.com:8080"
    method    = "GET"
    path      = "/web/cloudapi"
    timeout   = 12
    aone_name = "cloudapi-openapi"
  }

  request_parameters {
    name         = "aaa"
    type         = "STRING"
    required     = "OPTIONAL"
    in           = "QUERY"
    in_service   = "QUERY"
    name_service = "testparams"
  }

  stage_names = [
    "RELEASE",
    "TEST",
  ]
}


resource "alicloud_api_gateway_api" "pass" {
  name              = alicloud_api_gateway_group.apiGroup.name
  group_id          = alicloud_api_gateway_group.apiGroup.id
  description       = "your description"
  auth_type         = "APP"
  force_nonce_check = false

  request_config {
    protocol = "HTTPS"
    method   = "GET"
    path     = "/test/path1"
    mode     = "MAPPING"
  }

  service_type = "HTTP"

  http_service_config {
    address   = "https://apigateway-backend.alicloudapi.com:8080"
    method    = "GET"
    path      = "/web/cloudapi"
    timeout   = 12
    aone_name = "cloudapi-openapi"
  }

  request_parameters {
    name         = "aaa"
    type         = "STRING"
    required     = "OPTIONAL"
    in           = "QUERY"
    in_service   = "QUERY"
    name_service = "testparams"
  }

  stage_names = [
    "RELEASE",
    "TEST",
  ]
}
