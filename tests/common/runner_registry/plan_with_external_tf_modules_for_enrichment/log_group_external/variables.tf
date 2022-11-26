variable "create" {
  description = "Whether to create the Cloudwatch log group"
  type        = bool
  default     = true
}

variable "name" {
  description = "A name for the log group"
  type        = string
  default     = null
}

variable "name_prefix" {
  description = "A name prefix for the log group"
  type        = string
  default     = null
}

variable "retention_in_days" {
  description = "Specifies the number of days you want to retain log events in the specified log group"
  type        = number
  default     = null
}

variable "kms_key_id" {
  description = "The ARN of the KMS Key to use when encrypting logs"
  type        = string
  default     = null
}

variable "tags" {
  description = "A map of tags to add to Cloudwatch log group"
  type        = map(string)
  default     = {}
}
