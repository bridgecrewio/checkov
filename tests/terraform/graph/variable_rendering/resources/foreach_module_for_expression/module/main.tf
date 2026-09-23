variable "val" {
  type = string
}

resource "terraform_data" "test" {
  input = var.val
}
