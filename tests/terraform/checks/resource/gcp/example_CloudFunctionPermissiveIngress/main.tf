resource "google_cloudfunctions2_function" "pass1" {
  name = "gcf-function"
  location = "us-central1"
  description = "a new function"

  service_config {
    max_instance_count  = 3
    min_instance_count = 1
    available_memory    = "4Gi"
    timeout_seconds     = 60
    max_instance_request_concurrency = 80
    available_cpu = "4"
    environment_variables = {
        SERVICE_CONFIG_TEST = "config_test"
    }
    ingress_settings = "ALLOW_INTERNAL_ONLY"
    all_traffic_on_latest_revision = true
    service_account_email = google_service_account.account.email
  }
}

resource "google_cloudfunctions2_function" "fail1" {
  name = "gcf-function"
  location = "us-central1"
  description = "a new function"

  service_config {
    max_instance_count  = 3
    min_instance_count = 1
    available_memory    = "4Gi"
    timeout_seconds     = 60
    max_instance_request_concurrency = 80
    available_cpu = "4"
    environment_variables = {
        SERVICE_CONFIG_TEST = "config_test"
    }
    ingress_settings = "ALLOW_ALL"
    all_traffic_on_latest_revision = true
    service_account_email = google_service_account.account.email
  }
}

# Defaults to ALLOW_ALL (https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/cloudfunctions2_function#ingress_settings)
resource "google_cloudfunctions2_function" "fail2_not_specified" {
  name = "gcf-function"
  location = "us-central1"
  description = "a new function"

  service_config {
    max_instance_count  = 3
    min_instance_count = 1
    available_memory    = "4Gi"
    timeout_seconds     = 60
    max_instance_request_concurrency = 80
    available_cpu = "4"
    environment_variables = {
        SERVICE_CONFIG_TEST = "config_test"
    }
    all_traffic_on_latest_revision = true
    service_account_email = google_service_account.account.email
  }
}

resource "google_cloudfunctions_function" "pass2" {
  name                  = "serverless-lb-test-function"
  region                = "europe-west1"
  description           = "serverless-lb-test-function"
  available_memory_mb   = 512
  source_archive_bucket = google_storage_bucket.lb-zip.name
  source_archive_object = google_storage_bucket_object.lb-zip.name
  timeout               = 60
  service_account_email = google_service_account.serverless.email
  labels = {
    deployment-tool = "console-cloud"
  }
  entry_point           = "hello_get"
  runtime               = "python37"
  trigger_http = true
  ingress_settings = "ALLOW_INTERNAL_AND_GCLB"
}

resource "google_cloudfunctions_function" "fail3" {
  name                  = "serverless-lb-test-function"
  region                = "europe-west1"
  description           = "serverless-lb-test-function"
  available_memory_mb   = 512
  source_archive_bucket = google_storage_bucket.lb-zip.name
  source_archive_object = google_storage_bucket_object.lb-zip.name
  timeout               = 60
  service_account_email = google_service_account.serverless.email
  labels = {
    deployment-tool = "console-cloud"
  }
  entry_point           = "hello_get"
  runtime               = "python37"
  trigger_http = true
  ingress_settings = "ALLOW_ALL"
}
