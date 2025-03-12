resource "alicloud_oss_bucket" "fail" {
  bucket = "example-value"
  acl    = "public-read"
}

resource "alicloud_oss_bucket" "pass_simple" {
  bucket = "example-value"
  acl    = "private"
}

resource "alicloud_oss_bucket" "pass" {
  bucket = "example-value"
}

resource "alicloud_oss_bucket_acl" "pass" {
  bucket = alicloud_oss_bucket.pass.bucket
  acl    = "private"
}

resource "alicloud_oss_bucket" "fail2" {
  bucket = "example-value"
}

resource "alicloud_oss_bucket_acl" "fail2" {
  bucket = alicloud_oss_bucket.fail2.bucket
  acl    = "public-read"
}

resource "alicloud_oss_bucket" "pass_no_attach" {
  bucket = "example-value"
}
