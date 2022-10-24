# pass
resource "yandex_organizationmanager_organization_iam_binding" "pass-1" {
  organization_id = "some_organization_id"
  role = "viewer"
  members = [
    "userAccount:some_user_id",
  ]
}

resource "yandex_organizationmanager_organization_iam_member" "pass-2" {
  organization_id = "some_organization_id"
  role            = "viewer"
  member          = "userAccount:user_id"
}

# fail
resource "yandex_organizationmanager_organization_iam_binding" "fail-1" {
  organization_id = "some_organization_id"
  role = "organization-manager.organizations.owner"
  members = [
    "userAccount:some_user_id",
  ]
}

resource "yandex_organizationmanager_organization_iam_binding" "fail-2" {
  organization_id = "some_organization_id"
  role = "editor"
  members = [
    "userAccount:some_user_id",
  ]
}

resource "yandex_organizationmanager_organization_iam_binding" "fail-3" {
  organization_id = "some_organization_id"
  role = "admin"
  members = [
    "userAccount:some_user_id",
  ]
}

resource "yandex_organizationmanager_organization_iam_member" "fail-4" {
  organization_id = "some_organization_id"
  role            = "editor"
  member          = "userAccount:user_id"
}

resource "yandex_organizationmanager_organization_iam_member" "fail-5" {
  organization_id = "some_organization_id"
  role            = "admin"
  member          = "userAccount:user_id"
}

resource "yandex_organizationmanager_organization_iam_member" "fail-6" {
  organization_id = "some_organization_id"
  role            = "organization-manager.organizations.owner"
  member          = "userAccount:user_id"
}