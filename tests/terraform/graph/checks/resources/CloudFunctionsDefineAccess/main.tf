resource "google_cloudfunctions_function_iam_member" "member" {
  project = google_cloudfunctions_function.pass.project
  region = google_cloudfunctions_function.pass.region
  cloud_function = google_cloudfunctions_function.pass.name
  role = "roles/viewer"
  member = "user:jane@example.com"
}

resource "google_cloudfunctions_function" "pass" {
  name        = "function-test"
  description = "My function"
  runtime     = "nodejs16"

  available_memory_mb   = 128
  source_archive_bucket = google_storage_bucket.bucket.name
  source_archive_object = google_storage_bucket_object.archive.name
  trigger_http          = true
  entry_point           = "helloGET"
}

resource "google_cloudfunctions_function" "fail" {
  name        = "function-test"
  description = "My function"
  runtime     = "nodejs16"

  available_memory_mb   = 128
  source_archive_bucket = google_storage_bucket.bucket.name
  source_archive_object = google_storage_bucket_object.archive.name
  trigger_http          = true
  entry_point           = "helloGET"
}