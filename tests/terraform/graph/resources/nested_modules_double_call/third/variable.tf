variable "name" {
  type        = string
  description = "The Name of the application or solution  (e.g. `bastion` or `portal`)"
}

variable "namespace" {
  type        = string
  description = "Namespace, which could be your organization name or abbreviation, e.g. 'eg' or 'cp'"
  default     = ""
}

variable "stage" {
  type        = string
  description = "Stage (e.g. `prod`, `dev`, `staging`)"
  default     = ""
}

variable "environment" {
  type        = string
  default     = ""
  description = "Environment, e.g. 'prod', 'staging', 'dev', 'pre-prod', 'UAT'"
}

variable "attributes" {
  type        = list(string)
  description = "Additional attributes (e.g. `1`)"
  default     = []
}

variable "tags" {
  type        = map(string)
  description = "Additional tags (e.g. `map('BusinessUnit','XYZ')`)"
  default     = {}
}

variable "delimiter" {
  type        = string
  description = "Delimiter to be used between `name`, `namespace`, `stage`, etc."
  default     = "-"
}

variable "force_destroy" {
  type        = bool
  description = "Destroy the user even if it has non-Terraform-managed IAM access keys, login profile or MFA devices"
  default     = false
}

variable "path" {
  type        = string
  description = "Path in which to create the user"
  default     = "/"
}

variable "enabled" {
  type        = bool
  description = "Set to false to prevent the module from creating any resources"
  default     = true
}
