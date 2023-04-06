variable "other_var_2" {
  default = "abc"
}

resource "aws_s3_bucket" "my_bucket" {
  bucket = "${var.other_var_2}"
}