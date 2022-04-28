# pass
resource "yandex_storage_bucket" "pass" {
  bucket = "mybucket"

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        kms_master_key_id = "dsdasd1213123"
        sse_algorithm     = "aws:kms"
      }
    }
  }
}

# fail
resource "yandex_storage_bucket" "fail" {
  bucket = "mybucket"

}