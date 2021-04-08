variable "fqdn" {
  type        = string
  description = "FQDN of this instance of bazel-remote"
}

variable "elb_bucket" {
  type        = string
  description = "S3 bucket to keep ELB access logs"
}

variable "s3_bucket" {
  type        = string
  description = "The S3 bucket to be used as cache"
}

variable "iam_role" {
  type        = string
  description = "The IAM role to assume to access the S3 bucket"
}

variable "cache_size" {
  type        = number
  default     = 30
  description = "The amount of disk space to provision for caching"
}

variable "replicas" {
  type        = number
  default     = 8
  description = "The amount of bazel cache replicas to provision"
}

variable "namespace_dependency_link" {
  type = string
}

variable "namespace" {
  type = string
}
