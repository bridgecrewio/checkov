resource "google_container_registry" "pass1" {
  project  = "my-project"
  location = "EU"
}

resource "google_storage_bucket_iam_member" "pass1_member" {
  bucket = google_container_registry.pass1.id
  role = "roles/storage.objectViewer"
  member = "user:jason@example.com"
}

resource "google_container_registry" "pass2" {
  project  = "my-project"
  location = "EU"
}

resource "google_storage_bucket_iam_member" "pass2_member" {
  bucket = google_container_registry.pass2.id
  role = "roles/storage.objectViewer"
  member = "group:my-group@example.com"
}

resource "google_container_registry" "pass3" {
  project  = "my-project"
  location = "US"
}

resource "google_storage_bucket_iam_binding" "pass3_binding" {
  bucket = google_container_registry.pass3.id
  role = "roles/storage.admin"
  members = [
    "user:jane@example.com",
  ]
}

resource "google_container_registry" "pass4" {
  project  = "my-project"
  location = "US"
}

resource "google_storage_bucket_iam_binding" "pass4_binding" {
  bucket = google_container_registry.pass4.id
  role = "roles/storage.admin"
  members = [
    "user:jane@example.com",
    "domain:example.com",
    "group:my-group@example.com",
  ]
}

resource "google_container_registry" "fail1" {
  project  = "my-project"
  location = "EU"
}

resource "google_storage_bucket_iam_member" "fail1_member" {
  bucket = google_container_registry.fail1.id
  role = "roles/storage.objectViewer"
  member = "allUsers"
}

resource "google_container_registry" "fail2" {
  project  = "my-project"
  location = "EU"
}

resource "google_storage_bucket_iam_member" "fail2_member" {
  bucket = google_container_registry.fail2.id
  role = "roles/storage.objectViewer"
  member = "allAuthenticatedUsers"
}

resource "google_container_registry" "fail3" {
  project  = "my-project"
  location = "EU"
}

resource "google_storage_bucket_iam_binding" "fail3_binding" {
  bucket = google_container_registry.fail3.id
  role = "roles/storage.admin"
  members = [
    "allUsers",
  ]
}

resource "google_container_registry" "fail4" {
  project  = "my-project"
  location = "EU"
}

resource "google_storage_bucket_iam_binding" "fail4_binding" {
  bucket = google_container_registry.fail4.id
  role = "roles/storage.admin"
  members = [
    "allAuthenticatedUsers",
  ]
}

resource "google_container_registry" "fail5" {
  project  = "my-project"
  location = "EU"
}

resource "google_storage_bucket_iam_binding" "fail5_binding" {
  bucket = google_container_registry.fail5.id
  role = "roles/storage.admin"
  members = [
    "allAuthenticatedUsers",
    "group:my-group@example.com"
  ]
}

resource "google_container_registry" "fail6" {
  project  = "my-project"
  location = "EU"
}

resource "google_storage_bucket_iam_binding" "fail6_binding" {
  bucket = google_container_registry.fail6.id
  role = "roles/storage.admin"
  members = [
    "group:my-group@example.com",
    "allUsers",
    "user:jason@example.com",
  ]
}

resource "google_container_registry" "fail7" {
  project  = "my-project"
  location = "EU"
}

resource "google_storage_bucket_iam_binding" "fail7_binding" {
  bucket = google_container_registry.fail7.id
  role = "roles/storage.admin"
  members = [
    "allUsers",
    "group:my-group@example.com",
    "user:jason@example.com",
  ]
}

resource "google_container_registry" "fail8" {
  project  = "my-project"
  location = "EU"
}

resource "google_storage_bucket_iam_binding" "fail8_binding" {
  bucket = google_container_registry.fail8.id
  role = "roles/storage.admin"
  members = [
    "group:my-group@example.com",
    "user:jason@example.com",
    "allAuthenticatedUsers",
  ]
}
