resource "google_folder_iam_member" "owner" {
  folder  = "folders/1234567"
  role    = "roles/owner"
  member  = "user:jane@example.com"
}

resource "google_folder_iam_member" "editor" {
  folder  = "folders/1234567"
  role    = "roles/editor"
  member  = "user:jane@example.com"
}

resource "google_folder_iam_member" "viewer" {
  folder  = "folders/1234567"
  role    = "roles/viewer"
  member  = "user:jane@example.com"
}

resource "google_folder_iam_member" "other" {
  folder  = "folders/1234567"
  role    = "roles/other"
  member  = "user:jane@example.com"
}

resource "google_folder_iam_binding" "owner" {
  folder  = "folders/1234567"
  role    = "roles/owner"

  members = [
    "user:jane@example.com",
  ]
}

resource "google_folder_iam_binding" "editor" {
  folder  = "folders/1234567"
  role    = "roles/editor"

  members = [
    "user:jane@example.com",
  ]
}

resource "google_folder_iam_binding" "viewer" {
  folder  = "folders/1234567"
  role    = "roles/viewer"

  members = [
    "user:jane@example.com",
  ]
}

resource "google_folder_iam_binding" "other" {
  folder  = "folders/1234567"
  role    = "roles/other"

  members = [
    "user:jane@example.com",
  ]
}