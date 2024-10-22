variable "project_id" {
  type = string
}

locals {
    roles = [
        "roles/run.developer",
    ]
}

resource "google_project_iam_binding" "role" {
  for_each = toset(local.roles)
  project = var.project_id
  role    = each.key

  members = [
    "user:captain.america@marvel.com"
  ]
}
