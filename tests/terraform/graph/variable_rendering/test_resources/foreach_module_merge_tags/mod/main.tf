variable "name" { type = string }
variable "size" { type = string }
variable "vm_role" { type = string }
variable "tags" { type = map(string) }

resource "azurerm_windows_virtual_machine" "vm" {
  name = var.name
  size = var.size

  tags = merge(
    var.tags,
    {
      Role = var.vm_role
    }
  )
}
