variable "name" { type = string }
variable "location" { type = string }
variable "size" { type = string }
variable "zone" { type = string }
variable "tags" { type = map(string) }

resource "azurerm_windows_virtual_machine" "vm" {
  name     = var.name
  location = var.location
  size     = var.size
  zone     = var.zone
  tags     = var.tags
}
