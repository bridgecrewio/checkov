variable "foo" {}
variable "list_data" {}
variable "map_data" {}

resource "aws_s3_bucket" "my_bucket" {
  // TODO: List/map isn't resolving correctly
//  bucket = "${var.foo}-${var.list_data[0]}-${var.map_data[stage]}"
  bucket = var.foo
}