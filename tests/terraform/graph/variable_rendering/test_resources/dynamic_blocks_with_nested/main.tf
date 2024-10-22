resource "azuread_application" "bootstrap" {
  name                       = "test"
  type                       = "webapp/api"
  group_membership_claims    = "All"

  dynamic "required_resource_access" {
    for_each = var.required_resource_access
    content {
      resource_app_id = required_resource_access.value.resource_app_id

      dynamic "resource_access" {
        for_each = required_resource_access.value.resource_access
        content {
          id   = resource_access.value.id
          type = resource_access.value.type
        }
      }
    }
  }
  display_name = ""
}