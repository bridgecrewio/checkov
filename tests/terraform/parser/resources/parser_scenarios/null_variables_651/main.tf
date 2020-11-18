variable "logging_include_cookies" {
  type        = bool
  description = "Whether to enable cookies in access logging"
  default     = null
}

variable "logging_bucket_id" {
  type        = string
  description = "The bucket ID where to store access logs"
  default     = null
}

variable "logging_bucket_prefix" {
  type        = string
  description = "The prefix where to store access logs"
  default     = null
}

resource "aws_cloudfront_distribution" "cf_dis" {
  enabled           = true
  logging_config {
    include_cookies = var.logging_include_cookies
    bucket          = var.logging_bucket_id
    prefix          = var.logging_bucket_prefix
  }
}


resource "aws_s3_bucket" "website_bucket" {
  versioning {
      enabled = var.versioning
  }
}

variable "versioning" {
    default = null
}