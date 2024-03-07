## child/main.tf
variable "child-name" {
  type = string
}
resource "terraform_data" "child-example" {
  input = "1"
}
output "child-result" {
  value = terraform_data.child-example.output
}

