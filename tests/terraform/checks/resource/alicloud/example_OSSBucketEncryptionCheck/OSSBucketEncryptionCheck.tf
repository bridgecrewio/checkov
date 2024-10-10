## SHOULD PASS: OSS Bucket has server-side encryption enabled
resource "alicloud_oss_bucket" "ckv_unittest_pass" {
    bucket = "example-bucket"
    acl    = "private"

    server_side_encryption_rule {
        sse_algorithm = "AES256"
    }
}

## SHOULD FAIL: OSS Bucket does not have server-side encryption enabled
resource "alicloud_oss_bucket" "ckv_unittest_fail" {
    bucket = "example-bucket"
    acl    = "private"

    # Missing server_side_encryption_rule
}