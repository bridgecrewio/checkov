# pass
resource "yandex_storage_bucket" "pass" {
  bucket = "test-bucket"
  acl    = "private"
}

# fail
resource "yandex_storage_bucket" "fail-1" {
  bucket = "test-bucket"
  acl    = "public-read"
}

resource "yandex_storage_bucket" "fail-2" {
  bucket = "test-bucket"
  acl    = "public-read-write"
}

resource "yandex_storage_bucket" "fail-3" {
  bucket = "test-bucket"
  grant {
    type        = "Group"
    permissions = ["READ", "WRITE"]
    uri         = "http://acs.amazonaws.com/groups/global/AllUsers"
  }
}