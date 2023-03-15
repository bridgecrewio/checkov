# pass

resource "azurerm_storage_account" "pass" {
  name                     = "storageaccountname"
  resource_group_name      = "azurerm_resource_group.example.name"
  location                 = "azurerm_resource_group.example.location"
  account_tier             = "Standard"
  account_replication_type = "GRS"
}

resource "azurerm_storage_account" "pass_number" {
  name                     = 1234567890
  resource_group_name      = "azurerm_resource_group.example.name"
  location                 = "azurerm_resource_group.example.location"
  account_tier             = "Standard"
  account_replication_type = "GRS"
}

# fail

resource "azurerm_storage_account" "camel_case" {
  name                     = "thisIsWrong"
  resource_group_name      = "azurerm_resource_group.example.name"
  location                 = "azurerm_resource_group.example.location"
  account_tier             = "Standard"
  account_replication_type = "GRS"
}

resource "azurerm_storage_account" "kebab_case" {
  name                     = "this-is-wrong"
  resource_group_name      = "azurerm_resource_group.example.name"
  location                 = "azurerm_resource_group.example.location"
  account_tier             = "Standard"
  account_replication_type = "GRS"
}

resource "azurerm_storage_account" "too_long" {
  name                     = "thisiswayyyyyytoooloooong"
  resource_group_name      = "azurerm_resource_group.example.name"
  location                 = "azurerm_resource_group.example.location"
  account_tier             = "Standard"
  account_replication_type = "GRS"
}

# unknown

resource "azurerm_storage_account" "local" {
  name                     = "${local.prefix}example"
  resource_group_name      = "azurerm_resource_group.example.name"
  location                 = "azurerm_resource_group.example.location"
  account_tier             = "Standard"
  account_replication_type = "GRS"
}

resource "azurerm_storage_account" "module" {
  name                     = "${module.something.prefix}example"
  resource_group_name      = "azurerm_resource_group.example.name"
  location                 = "azurerm_resource_group.example.location"
  account_tier             = "Standard"
  account_replication_type = "GRS"
}

resource "azurerm_storage_account" "var" {
  name                     = "${var.prefix}example"
  resource_group_name      = "azurerm_resource_group.example.name"
  location                 = "azurerm_resource_group.example.location"
  account_tier             = "Standard"
  account_replication_type = "GRS"
}

resource "azurerm_storage_account" "random_string" {
  name                     = "${random_string.prefix}example"
  resource_group_name      = "azurerm_resource_group.example.name"
  location                 = "azurerm_resource_group.example.location"
  account_tier             = "Standard"
  account_replication_type = "GRS"
}

resource "azurerm_storage_account" "random_id" {
  name                     = "${random_id.prefix}example"
  resource_group_name      = "azurerm_resource_group.example.name"
  location                 = "azurerm_resource_group.example.location"
  account_tier             = "Standard"
  account_replication_type = "GRS"
}

resource "azurerm_storage_account" "random_pet" {
  name                     = "${random_pet.prefix}example"
  resource_group_name      = "azurerm_resource_group.example.name"
  location                 = "azurerm_resource_group.example.location"
  account_tier             = "Standard"
  account_replication_type = "GRS"
}

resource "azurerm_storage_account" "random_integer" {
  name                     = "${random_integer.prefix}example"
  resource_group_name      = "azurerm_resource_group.example.name"
  location                 = "azurerm_resource_group.example.location"
  account_tier             = "Standard"
  account_replication_type = "GRS"
}


