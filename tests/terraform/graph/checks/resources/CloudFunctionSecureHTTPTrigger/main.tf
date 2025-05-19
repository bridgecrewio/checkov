resource "google_cloudfunctions_function" "pass" {
  name        = "function-test"
  description = "My function"
  runtime     = "nodejs16"

  available_memory_mb          = 128
  source_archive_bucket        = google_storage_bucket.bucket.name
  source_archive_object        = google_storage_bucket_object.archive.name
  trigger_http                 = true
  https_trigger_security_level = "SECURE_ALWAYS"
  timeout                      = 60
  entry_point                  = "helloGET"
  labels = {
    my-label = "my-label-value"
  }
}

resource "google_cloudfunctions_function" "pass_1" {
  name        = "pubsub-trigger-test"
  description = "My function"
  runtime     = "nodejs16"

  available_memory_mb          = 128
  source_archive_bucket        = google_storage_bucket.bucket.name
  source_archive_object        = google_storage_bucket_object.archive.name
  #event_trigger should not require "https_trigger_security_level"
  event_trigger                {
    event_type = "google.cloud.pubsub.topic.v1.messagePublished"
    resource = "projects/triggering-projects/topics/trigger"
  }
  timeout                      = 60
  entry_point                  = "helloGET"
  labels = {
    my-label = "my-label-value"
  }
}

resource "google_cloudfunctions_function" "pass_2" {
  name        = "pubsub-trigger-test"
  description = "My function"
  runtime     = "nodejs16"

  available_memory_mb          = 128
  source_archive_bucket        = google_storage_bucket.bucket.name
  source_archive_object        = google_storage_bucket_object.archive.name
  #event_trigger should not require "https_trigger_security_level"
  trigger_http                 = false
  timeout                      = 60
  entry_point                  = "helloGET"
  labels = {
    my-label = "my-label-value"
  }
}

resource "google_cloudfunctions_function" "fail_1" {
  name        = "function-test"
  description = "My function"
  runtime     = "nodejs16"

  available_memory_mb          = 128
  source_archive_bucket        = google_storage_bucket.bucket.name
  source_archive_object        = google_storage_bucket_object.archive.name
  trigger_http                 = true
  https_trigger_security_level = "SECURE_OPTIONAL"
  timeout                      = 60
  entry_point                  = "helloGET"
  labels = {
    my-label = "my-label-value"
  }
}

resource "google_cloudfunctions_function" "fail_2" {
  name        = "function-test"
  description = "My function"
  runtime     = "nodejs16"

  available_memory_mb          = 128
  source_archive_bucket        = google_storage_bucket.bucket.name
  source_archive_object        = google_storage_bucket_object.archive.name
  trigger_http                 = true
  timeout                      = 60
  entry_point                  = "helloGET"
  labels = {
    my-label = "my-label-value"
  }
}