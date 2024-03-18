# modules.tf
module "modules" {
  count = 12
  source = "./parent"
  parent   = count.index
}
output "modules-result" {
  value = { for k, v in module.modules-parent : k => v }
}