variable "foo" {}
variable "list_data" {}
variable "map_data" {}
variable "only_here" {
  default = "hello"
}
variable "other_var_1" {
  default = "abc"
}
variable "other_var_2" {
  default = "abc"
}
variable "other_var_3" {
  default = "abc"
}

resource "aws_s3_bucket" "my_bucket" {
  bucket = "${var.only_here}-${var.foo}-${var.list_data[0]}-${var.map_data[stage]}-${var.other_var_1}-${var.other_var_2}-${var.other_var_3}"
}