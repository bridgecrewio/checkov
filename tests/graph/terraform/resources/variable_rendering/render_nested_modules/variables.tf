variable "bucket_name" {
  default = {
    val = "MyBucket"
  }

}

variable "acl" {
  default = var.acl_default_value
}

variable "acl_default_value" {
  default = local.x.y
}

variable "region" {
  default = "us-west-2"
}

variable "aws_profile" {
  default = "default"
}

variable "dummy_1" {
  default = "dummy_1"
}

