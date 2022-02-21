
resource "google_storage_bucket" "fail" {
  name     = "foo"
  location = "EU"

  versioning = {
    enabled = false
  }
}

resource "google_storage_bucket" "fail2" {
  name     = "foo"
  location = "EU"
}

resource "google_storage_bucket" "pass" {
  name     = "foo"
  location = "EU"

  versioning = {
    enabled = true
  }
}