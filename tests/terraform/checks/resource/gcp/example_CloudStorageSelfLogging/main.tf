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

# unknown - log_bucket is a computed value, absent from plan JSON

resource "google_storage_bucket" "unknown" {
  name     = "my-bucket"
  location = "EU"

  logging {
    log_object_prefix = "my-prefix/"
  }
}
