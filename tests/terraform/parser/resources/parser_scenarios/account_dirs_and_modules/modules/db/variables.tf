variable "DB_DELETION_PROTECTION" {
  default     = true
}

variable "ENGINE_VERSION" {
  default     = "9.5"
}

variable "DB_INSTANCE_TYPE" {
  default     = "db.t3.medium"
}

variable "ENCRYPTED" {}