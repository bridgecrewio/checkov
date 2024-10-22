variable "rg_name" {
  type    = string
  default = "abc-azr-lab"
}

variable "rg_location" {
  type    = string
  default = "East US"
}

variable "vnet_name" {
  type    = string
  default = "dynamic_vnet"
}

variable "nsg_name_fail" {
  type    = string
  default = "dynamic_nsg_fail"
}

variable "nsg_name_pass" {
  type    = string
  default = "dynamic_nsg_pass"
}

variable "tags" {
  type    = list(string)
  default = ["testing", "dynamic_block"]
}

variable "address_space" {
  type    = list(string)
  default = ["10.100.0.0/16"]
}

variable "subnet_list" {
  type = list(object({
    name           = string
    address_prefix = string
    security_group = string
  }))
  description = "Values for each subnet"
}

variable "fail_nsg_rules" {
  type = list(object({
    name                       = string
    priority                   = number
    direction                  = string
    access                     = string
    protocol                   = string
    source_port_range          = string
    destination_port_range     = string
    source_address_prefix      = string
    destination_address_prefix = string
  }))
  description = "Values for each NSG rule"
}

variable "pass_nsg_rules" {
  type = list(object({
    name                       = string
    priority                   = number
    direction                  = string
    access                     = string
    protocol                   = string
    source_port_range          = string
    destination_port_range     = string
    source_address_prefix      = string
    destination_address_prefix = string
  }))
  description = "Values for each NSG rule"
}