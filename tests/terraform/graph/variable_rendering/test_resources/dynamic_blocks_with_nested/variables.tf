variable required_resource_access {
  type = list(object({
    resource_app_id = string
    resource_access = list(object({
      id   = string
      type = string
    }))
  }))

  default = [{
    resource_app_id = "00000003-0000-0000-c000-000000000000"
    resource_access = [{
      id   = "7ab1d382-f21e-4acd-a863-ba3e13f7da61"
      type = "Role"
    }]
  }]
}