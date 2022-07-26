variable "bucket_name" {

}

variable "ebs_size" {

}

resource "aws_s3_bucket" "pass1" {
  bucket        = var.bucket_name
}

resource "aws_s3_bucket" "pass2" {
  bucket        = "${var.bucket_name}-abc"
}

resource "aws_s3_bucket" "pass3" {
  bucket        = "abc-${var.bucket_name}"
}
