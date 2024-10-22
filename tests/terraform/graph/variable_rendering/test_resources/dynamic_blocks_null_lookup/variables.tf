variable "name" {
  type        = string
  description = "(Required, Forces new resource) The name of the security group."
}

variable "description" {
  type        = string
  description = "(Optional, Forces new resource) The security group description. Defaults to 'Managed by Terraform'. Cannot be \"\". NOTE: This field maps to the AWS GroupDescription attribute, for which there is no Update API. If you'd like to classify your security groups in a way that can be updated, use tags."
  default     = "Managed by Terraform"
}

variable "ingress" {
  type        = any
  description = "(Optional) Can be specified multiple times for each ingress rule. Each ingress block supports fields documented below. This argument is processed in <a href='https://www.terraform.io/docs/configuration/attr-as-blocks.html'>attribute-as-blocks</a> mode."
  default = [
  ]
}

variable "egress" {
  type        = any
  description = "(Optional, VPC only) Can be specified multiple times for each egress rule. Each egress block supports fields documented below. This argument is processed in <a href='https://www.terraform.io/docs/configuration/attr-as-blocks.html'>attribute-as-blocks</a> mode."
  default = [
  ]
}

variable "revoke_rules_on_delete" {
  type        = bool
  description = "(Optional) Instruct Terraform to revoke all of the Security Groups attached ingress and egress rules before deleting the rule itself. This is normally not needed, however certain AWS services such as Elastic Map Reduce may automatically add required rules to security groups used with the service, and those rules may contain a cyclic dependency that prevent the security groups from being destroyed without removing the dependency first. Default false"
  default     = false
}

variable "vpc_id" {
  type        = string
  description = "(Required, Forces new resource) The VPC ID."
}

variable "tags" {
  type        = map(string)
  description = "Map of tags to add to the resources"
  default     = {}
}