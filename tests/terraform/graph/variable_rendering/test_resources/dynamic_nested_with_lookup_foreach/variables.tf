variable "artifact_store" {
  description = "Map to populate the artifact block"
  type        = map(any)
}

variable "name" {
  type = string
}

variable "role_arn" {
  type        = string
  description = "Optionally supply an existing role"
  default     = ""
}

variable "stages" {
  type        = list(any)
  description = "This list describes each stage of the build"
}

variable "description" {
  type        = string
  description = "Description of build project"
}

variable "common_tags" {
  type        = map(any)
  description = "Implements the common tags scheme"
}

variable "policypath" {
  default     = ""
  type        = string
  description = ""
}


variable "kms_key_arn" {
  type = string
}