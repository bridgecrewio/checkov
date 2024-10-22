resource "google_storage_bucket" "inherited" {
  name                     = "foo"
  location                 = "EU"
  public_access_prevention = "inherited"
}

resource "google_storage_bucket" "default" {
  name                     = "foo"
  location                 = "EU"
}

resource "google_storage_bucket" "enforced" {
  name                     = "foo"
  location                 = "EU"
  public_access_prevention = "enforced"
}