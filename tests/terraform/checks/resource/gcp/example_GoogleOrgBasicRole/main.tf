resource "google_organization_iam_member" "owner" {
  org_id  = "your-organization-id"
  role    = "roles/owner"
  member  = "user:jane@example.com"
}

resource "google_organization_iam_member" "editor" {
  org_id  = "your-organization-id"
  role    = "roles/editor"
  member  = "user:jane@example.com"
}

resource "google_organization_iam_member" "viewer" {
  org_id  = "your-organization-id"
  role    = "roles/viewer"
  member  = "user:jane@example.com"
}

resource "google_organization_iam_member" "other" {
  org_id  = "your-organization-id"
  role    = "roles/other"
  member  = "user:jane@example.com"
}

resource "google_organization_iam_binding" "owner" {
  org_id  = "your-organization-id"
  role    = "roles/owner"

  members = [
    "user:jane@example.com",
  ]
}

resource "google_organization_iam_binding" "editor" {
  org_id  = "your-organization-id"
  role    = "roles/editor"

  members = [
    "user:jane@example.com",
  ]
}

resource "google_organization_iam_binding" "viewer" {
  org_id  = "your-organization-id"
  role    = "roles/viewer"

  members = [
    "user:jane@example.com",
  ]
}

resource "google_organization_iam_binding" "other" {
  org_id  = "your-organization-id"
  role    = "roles/other"

  members = [
    "user:jane@example.com",
  ]
}