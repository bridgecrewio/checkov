resource "alicloud_oss_bucket" "good-bucket" {
  bucket = "bucket-170309-acl"
  acl    = "private"
}

resource "alicloud_oss_bucket" "good-bucket2" {
  bucket = "bucket-170309-acl"
}

resource "alicloud_oss_bucket" "bad-bucket" {
  bucket = "bucket-170309-acl"
  acl    = "public-read-write"
}

resource "alicloud_oss_bucket" "bad-bucket2" {
  bucket = "bucket-170309-acl"
  acl    = "public-read"
}