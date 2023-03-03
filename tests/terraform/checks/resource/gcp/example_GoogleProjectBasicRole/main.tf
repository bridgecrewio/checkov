resource "google_project_iam_member" "owner" {
  project  = "your-project-id"
  role    = "roles/owner"
  member  = "user:jane@example.com"
}

resource "google_project_iam_member" "editor" {
  project  = "your-project-id"
  role    = "roles/editor"
  member  = "user:jane@example.com"
}

resource "google_project_iam_member" "viewer" {
  project  = "your-project-id"
  role    = "roles/viewer"
  member  = "user:jane@example.com"
}

resource "google_project_iam_member" "other" {
  project  = "your-project-id"
  role    = "roles/other"
  member  = "user:jane@example.com"
}

resource "google_project_iam_binding" "owner" {
  project  = "your-project-id"
  role    = "roles/owner"

  members = [
    "user:jane@example.com",
  ]
}

resource "google_project_iam_binding" "editor" {
  project  = "your-project-id"
  role    = "roles/editor"

  members = [
    "user:jane@example.com",
  ]
}

resource "google_project_iam_binding" "viewer" {
  project  = "your-project-id"
  role    = "roles/viewer"

  members = [
    "user:jane@example.com",
  ]
}

resource "google_project_iam_binding" "other" {
  project  = "your-project-id"
  role    = "roles/other"

  members = [
    "user:jane@example.com",
  ]
}