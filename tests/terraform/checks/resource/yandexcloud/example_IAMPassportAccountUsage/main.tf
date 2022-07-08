# pass
resource "yandex_resourcemanager_folder_iam_binding" "pass" {
  role = "alb.viewer"
  members = [
    "serviceAccount:some_user_id1",
    "serviceAccount:some_user_id2",
    "serviceAccount:some_user_id3",
    "serviceAccount:some_user_id4",
  ]
}

resource "yandex_resourcemanager_folder_iam_member" "pass" {
  role   = "k8s.admin"
  member = "serviceAccount:user_id"
}

resource "yandex_resourcemanager_cloud_iam_binding" "pass" {
  role = "editor"
  members = [
    "serviceAccount:some_user_id",
  ]
}

resource "yandex_resourcemanager_cloud_iam_member" "pass" {
  role     = "alb.admin"
  member   = "federatedUser:user_id"
}

resource "yandex_organizationmanager_organization_iam_binding" "pass" {
  role = "viewer"
  members = [
    "federatedUser:some_user_id",
  ]
}

resource "yandex_organizationmanager_organization_iam_member" "pass" {
  role            = "editor"
  member          = "federatedUser:user_id"
}

# fail
resource "yandex_resourcemanager_folder_iam_binding" "fail" {
  role = "alb.viewer"
  members = [
    "userAccount:some_user_id",
    "serviceAccount:some_user_id",
  ]
}

resource "yandex_resourcemanager_folder_iam_member" "fail" {
  role   = "k8s.admin"
  member = "userAccount:user_id"
}

resource "yandex_resourcemanager_cloud_iam_binding" "fail" {
  role = "editor"
  members = [
    "userAccount:some_user_id",
    "serviceAccount:some_user_id",
  ]
}

resource "yandex_resourcemanager_cloud_iam_member" "fail" {
  role     = "alb.admin"
  member   = "userAccount:user_id"
}

resource "yandex_organizationmanager_organization_iam_binding" "fail" {
  role = "viewer"
  members = [
    "userAccount:some_user_id",
  ]
}

resource "yandex_organizationmanager_organization_iam_member" "fail" {
  role            = "editor"
  member          = "userAccount:user_id"
}