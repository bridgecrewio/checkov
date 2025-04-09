variable "instance_type" {
  default = "t3.small"
}

variable "key_name" {
  type = string
}

variable "vmhosts" {
  description = "VM hosts with configuration"
  type = list(object({
    name           = string
    monitoring     = bool
    tags           = map(string)
    private_ip     = string
    ports          = list(number)
  }))
}