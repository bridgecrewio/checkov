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
  description = "Specifies the number of days you want to retain log events in the specified log group. Possible values are: 1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1827, and 3653."
  type        = number
  default     = null

  validation {
    condition     = var.retention_in_days == null ? true : contains([0, 1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1827, 3653], var.retention_in_days)
    error_message = "Must be 1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1827, 3653 or 0 (zero indicates never expire logs)."
  }
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
