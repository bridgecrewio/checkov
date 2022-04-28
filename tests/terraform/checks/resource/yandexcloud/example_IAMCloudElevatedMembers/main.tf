# pass
resource "yandex_resourcemanager_cloud_iam_member" "pass-1" {
  role     = "viewer"
  member   = "userAccount:user_id"
}

resource "yandex_resourcemanager_cloud_iam_member" "pass-2" {
  role     = "alb.admin"
  member   = "userAccount:user_id"
}

resource "yandex_resourcemanager_cloud_iam_binding" "pass-3" {
  role = "viewer"
  members = [
    "userAccount:some_user_id",
  ]
}

# fail
resource "yandex_resourcemanager_cloud_iam_member" "fail-1" {
  role     = "editor"
  member   = "userAccount:user_id"
}

resource "yandex_resourcemanager_cloud_iam_binding" "fail-2" {
  role = "editor"
  members = [
    "userAccount:some_user_id",
  ]
}