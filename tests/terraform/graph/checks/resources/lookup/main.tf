provider "aws" {
    region="us-east-1"
}

resource "aws_sns_topic" "sns" {
    name = "nc-sns-local"
    kms_master_key_id = "alias/aws/sns"
}

locals {
    protocol1 = var.nc_local_sns
    endpoint1 = var.nc_local_endpoint
}

resource "aws_sns_topic_subscription" "sample_nc_local" {
  topic_arn = aws_sns_topic.sns.arn
  protocol  = lookup({a=local.protocol1}, "a", "https")
  endpoint  = lookup({a=local.endpoint1}, "a", "https://www.example.com")
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
