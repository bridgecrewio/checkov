# pass

resource "google_storage_bucket" "pass" {
  name     = "example"
  location = "EU"

  logging {
    log_bucket = "other.com"
  }
}

# fail

resource "google_storage_bucket" "fail" {
  name     = "example.com"
  location = "EU"

  logging {
    log_bucket = "example.com"
  }
}
