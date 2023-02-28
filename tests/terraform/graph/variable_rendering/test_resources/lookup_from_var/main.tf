locals {
    protocol1 = var.nc_local_sns
    endpoint1 = var.nc_local_endpoint
}

resource "aws_sns_topic_subscription" "sample_nc_local" {
  protocol  = lookup({a=local.protocol1}, "a", "https")
  endpoint  = lookup({a=local.endpoint1}, "a", "https://www.example.com")
  topic_arn = ""
}

variable "nc_local_sns" {
    type = string
    description = "(optional) describe your variable"
    default = "http"
}
variable "nc_local_endpoint" {
    type = string
    description = "(optional) describe your variable"
    default = "http://www.example.com"
}
