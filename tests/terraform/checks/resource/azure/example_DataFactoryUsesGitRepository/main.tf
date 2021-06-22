# pass

resource "azurerm_data_factory" "github" {
  location            = azurerm_resource_group.example.location
  name                = "example"
  resource_group_name = azurerm_resource_group.example.name

  github_configuration {
    account_name    = "bridgecrewio"
    branch_name     = "master"
    git_url         = "https://github.com"
    repository_name = "checkov"
    root_folder     = "/"
  }
}

resource "azurerm_data_factory" "vsts" {
  location            = azurerm_resource_group.example.location
  name                = "example"
  resource_group_name = azurerm_resource_group.example.name

  vsts_configuration {
    account_name    = "bridgecrewio"
    branch_name     = "master"
    project_name    = "chechov"
    repository_name = "checkov"
    root_folder     = "/"
    tenant_id       = "123456789"
  }
}

# fail

resource "azurerm_data_factory" "fail" {
  location            = azurerm_resource_group.example.location
  name                = "example"
  resource_group_name = azurerm_resource_group.example.name
}
