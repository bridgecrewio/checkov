variable "acl" {
  type        = string
  default     = "private"
  description = "The [canned ACL](https://docs.aws.amazon.com/AmazonS3/latest/dev/acl-overview.html#canned-acl) to apply. We recommend `private` to avoid exposing sensitive information. Conflicts with `grants`."
}

variable "grants" {
  type = list(object({
    id          = string
    type        = string
    permissions = list(string)
    uri         = string
  }))
  default = null

  description = "A list of ACL policy grants. Conflicts with `acl`. Set `acl` to `null` to use this."
}

variable "policy" {
  type        = string
  default     = ""
  description = "A valid bucket policy JSON document. Note that if the policy document is not specific enough (but still valid), Terraform may view the policy as constantly changing in a terraform plan. In this case, please make sure you use the verbose/specific version of the policy"
}

variable "region" {
  type        = string
  default     = ""
  description = "If specified, the AWS region this bucket should reside in. Otherwise, the region used by the callee"
}

variable "force_destroy" {
  type        = bool
  default     = false
  description = "A boolean string that indicates all objects should be deleted from the bucket so that the bucket can be destroyed without error. These objects are not recoverable"
}

variable "versioning_enabled" {
  type        = bool
  default     = false
  description = "A state of versioning. Versioning is a means of keeping multiple variants of an object in the same bucket"
}

variable "sse_algorithm" {
  type        = string
  default     = "AES256"
  description = "The server-side encryption algorithm to use. Valid values are `AES256` and `aws:kms`"
}

variable "kms_master_key_arn" {
  type        = string
  default     = ""
  description = "The AWS KMS master key ARN used for the `SSE-KMS` encryption. This can only be used when you set the value of `sse_algorithm` as `aws:kms`. The default aws/s3 AWS KMS master key is used if this element is absent while the `sse_algorithm` is `aws:kms`"
}

variable "user_enabled" {
  type        = bool
  default     = false
  description = "Set to `true` to create an IAM user with permission to access the bucket"
}

variable "allowed_bucket_actions" {
  type        = list(string)
  default     = ["s3:PutObject", "s3:PutObjectAcl", "s3:GetObject", "s3:DeleteObject", "s3:ListBucket", "s3:ListBucketMultipartUploads", "s3:GetBucketLocation", "s3:AbortMultipartUpload"]
  description = "List of actions the user is permitted to perform on the S3 bucket"
}

variable "allow_encrypted_uploads_only" {
  type        = bool
  default     = false
  description = "Set to `true` to prevent uploads of unencrypted objects to S3 bucket"
}

variable "lifecycle_rule_enabled" {
  type        = bool
  default     = false
  description = "Enable or disable lifecycle rule"
}

variable "prefix" {
  type        = string
  default     = ""
  description = "Prefix identifying one or more objects to which the rule applies"
}

variable "noncurrent_version_transition_days" {
  type        = number
  default     = 30
  description = "Number of days to persist in the standard storage tier before moving to the glacier tier infrequent access tier"
}

variable "noncurrent_version_expiration_days" {
  type        = number
  default     = 90
  description = "Specifies when noncurrent object versions expire"
}

variable "cors_rule_inputs" {
  type = list(object({
    allowed_headers = list(string)
    allowed_methods = list(string)
    allowed_origins = list(string)
    expose_headers  = list(string)
    max_age_seconds = number
  }))
  default = null

  description = "Specifies the allowed headers, methods, origins and exposed headers when using CORS on this bucket"
}

variable "standard_transition_days" {
  type        = number
  default     = 30
  description = "Number of days to persist in the standard storage tier before moving to the infrequent access tier"
}

variable "glacier_transition_days" {
  type        = number
  default     = 60
  description = "Number of days after which to move the data to the glacier storage tier"
}

variable "enable_glacier_transition" {
  type        = bool
  default     = true
  description = "Enables the transition to AWS Glacier which can cause unnecessary costs for huge amount of small files"
}

variable "enable_standard_ia_transition" {
  type        = bool
  default     = false
  description = "Enables the transition to STANDARD_IA"
}

variable "expiration_days" {
  type        = number
  default     = 90
  description = "Number of days after which to expunge the objects"
}

variable "abort_incomplete_multipart_upload_days" {
  type        = number
  default     = 5
  description = "Maximum time (in days) that you want to allow multipart uploads to remain in progress"
}

variable "lifecycle_tags" {
  type        = map(string)
  description = "Tags filter. Used to manage object lifecycle events"
  default     = {}
}

variable "block_public_acls" {
  type        = bool
  default     = true
  description = "Set to `false` to disable the blocking of new public access lists on the bucket"
}

variable "block_public_policy" {
  type        = bool
  default     = true
  description = "Set to `false` to disable the blocking of new public policies on the bucket"
}

variable "ignore_public_acls" {
  type        = bool
  default     = true
  description = "Set to `false` to disable the ignoring of public access lists on the bucket"
}

variable "restrict_public_buckets" {
  type        = bool
  default     = true
  description = "Set to `false` to disable the restricting of making the bucket public"
}
