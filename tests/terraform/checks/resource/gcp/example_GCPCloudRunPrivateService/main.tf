################
## PASS TESTS ##
################

resource "google_cloud_run_service_iam_binding" "pass1" {
  location = google_cloud_run_service.default.location
  service = google_cloud_run_service.default.name
  role = "roles/viewer"
  members = [
    "user:jane@example.com",
    "group:mygroup@example.com",
  ]
}

resource "google_cloud_run_service_iam_binding" "pass2" {
  location = google_cloud_run_service.default.location
  service = google_cloud_run_service.default.name
  role = "roles/viewer"
  members = [
    "user:jason@example.com",
  ]
}

resource "google_cloud_run_service_iam_member" "pass1" {
  location = google_cloud_run_service.default.location
  service = google_cloud_run_service.default.name
  role = "roles/viewer"
  member = "user:jane@example.com"
}

resource "google_cloud_run_service_iam_member" "pass2" {
  location = google_cloud_run_service.default.location
  service = google_cloud_run_service.default.name
  role = "roles/viewer"
  member = "domain:example.com"
}

################
## FAIL TESTS ##
################

resource "google_cloud_run_service_iam_binding" "fail1" {
  location = google_cloud_run_service.default.location
  service = google_cloud_run_service.default.name
  role = "roles/viewer"
  members = [
    "allAuthenticatedUsers",
  ]
}

resource "google_cloud_run_service_iam_binding" "fail2" {
  location = google_cloud_run_service.default.location
  service = google_cloud_run_service.default.name
  role = "roles/viewer"
  members = [
    "allUsers",
  ]
}

resource "google_cloud_run_service_iam_binding" "fail3" {
  location = google_cloud_run_service.default.location
  service = google_cloud_run_service.default.name
  role = "roles/viewer"
  members = [
    "allUsers",
    "user:jason@example.com",
  ]
}

resource "google_cloud_run_service_iam_binding" "fail4" {
  location = google_cloud_run_service.default.location
  service = google_cloud_run_service.default.name
  role = "roles/viewer"
  members = [
    "user:jason@example.com",
    "allAuthenticatedUsers",
  ]
}

resource "google_cloud_run_service_iam_binding" "fail5" {
  location = google_cloud_run_service.default.location
  service = google_cloud_run_service.default.name
  role = "roles/viewer"
  members = [
    "user:jason@example.com",
    "allAuthenticatedUsers",
    "domain:example.com",
  ]
}

resource "google_cloud_run_service_iam_member" "fail1" {
  location = google_cloud_run_service.default.location
  service = google_cloud_run_service.default.name
  role = "roles/viewer"
  member  = "allAuthenticatedUsers"
}

resource "google_cloud_run_service_iam_member" "fail2" {
  location = google_cloud_run_service.default.location
  service = google_cloud_run_service.default.name
  role = "roles/viewer"
  member  = "allUsers"
}
