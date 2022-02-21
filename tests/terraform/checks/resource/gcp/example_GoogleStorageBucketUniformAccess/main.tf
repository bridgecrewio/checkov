# pass

resource "google_storage_bucket" "enabled" {
  name     = "example"
  location = "EU"

  uniform_bucket_level_access = True
}

# fail

resource "google_storage_bucket" "default" {
  name     = "example.com"
  location = "EU"
}

resource "google_storage_bucket" "disabled" {
  name     = "example"
  location = "EU"

  uniform_bucket_level_access = False
}
