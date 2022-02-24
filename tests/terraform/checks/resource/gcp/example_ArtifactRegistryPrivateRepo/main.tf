################
## PASS TESTS ##
################

resource "google_artifact_registry_repository_iam_binding" "pass1" {
  provider = google-beta
  location = google_artifact_registry_repository.my-repo.location
  repository = google_artifact_registry_repository.my-repo.name
  role = "roles/viewer"
  members = [
    "user:jane@example.com",
    "group:mygroup@example.com",
  ]
}

resource "google_artifact_registry_repository_iam_binding" "pass2" {
  provider = google-beta
  location = google_artifact_registry_repository.my-repo.location
  repository = google_artifact_registry_repository.my-repo.name
  role = "roles/viewer"
  members = [
    "user:jason@example.com",
  ]
}

resource "google_artifact_registry_repository_iam_member" "pass1" {
  provider = google-beta
  location = google_artifact_registry_repository.my-repo.location
  repository = google_artifact_registry_repository.my-repo.name
  role = "roles/viewer"
  member = "user:jane@example.com"
}

resource "google_artifact_registry_repository_iam_member" "pass2" {
  provider = google-beta
  location = google_artifact_registry_repository.my-repo.location
  repository = google_artifact_registry_repository.my-repo.name
  role = "roles/viewer"
  member = "domain:example.com"
}

################
## FAIL TESTS ##
################

resource "google_artifact_registry_repository_iam_binding" "fail1" {
  provider = google-beta
  location = google_artifact_registry_repository.my-repo.location
  repository = google_artifact_registry_repository.my-repo.name
  role = "roles/viewer"
  members = [
    "allAuthenticatedUsers",
  ]
}

resource "google_artifact_registry_repository_iam_binding" "fail2" {
  provider = google-beta
  location = google_artifact_registry_repository.my-repo.location
  repository = google_artifact_registry_repository.my-repo.name
  role = "roles/viewer"
  members = [
    "allUsers",
  ]
}

resource "google_artifact_registry_repository_iam_binding" "fail3" {
  provider = google-beta
  location = google_artifact_registry_repository.my-repo.location
  repository = google_artifact_registry_repository.my-repo.name
  role = "roles/viewer"
  members = [
    "allUsers",
    "user:jason@example.com",
  ]
}

resource "google_artifact_registry_repository_iam_binding" "fail4" {
  provider = google-beta
  location = google_artifact_registry_repository.my-repo.location
  repository = google_artifact_registry_repository.my-repo.name
  role = "roles/viewer"
  members = [
    "user:jason@example.com",
    "allAuthenticatedUsers",
  ]
}

resource "google_artifact_registry_repository_iam_binding" "fail5" {
  provider = google-beta
  location = google_artifact_registry_repository.my-repo.location
  repository = google_artifact_registry_repository.my-repo.name
  role = "roles/viewer"
  members = [
    "user:jason@example.com",
    "allAuthenticatedUsers",
    "domain:example.com",
  ]
}

resource "google_artifact_registry_repository_iam_member" "fail1" {
  provider = google-beta
  location = google_artifact_registry_repository.my-repo.location
  repository = google_artifact_registry_repository.my-repo.name
  role = "roles/viewer"
  member  = "allAuthenticatedUsers"
}

resource "google_artifact_registry_repository_iam_member" "fail2" {
  provider = google-beta
  location = google_artifact_registry_repository.my-repo.location
  repository = google_artifact_registry_repository.my-repo.name
  role = "roles/viewer"
  member  = "allUsers"
}
