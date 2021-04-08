resource "azurerm_data_factory" "data_factory_good" {
  name                = "example"
  location            = "location"
  resource_group_name = "group"
}

resource "azurerm_data_factory" "data_factory_bad" {
  name                = "example"
  location            = "location"
  resource_group_name = "group"
}

resource "azurerm_data_factory_linked_service_key_vault" "factory_good" {
  name                = "example"
  resource_group_name = "example"
  data_factory_name   = azurerm_data_factory.data_factory_good.name
  key_vault_id        = "123456"
}