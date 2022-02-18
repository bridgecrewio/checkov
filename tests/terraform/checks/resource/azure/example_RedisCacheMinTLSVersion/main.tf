resource "azurerm_redis_cache" "pass" {
  name                = "timeout-redis"
  location            = "West Europe"
  resource_group_name = azurerm_resource_group.example_rg.name
  subnet_id           = azurerm_subnet.example_redis_snet.id

  family      = "P"
  capacity    = 1
  sku_name    = "Premium"
  shard_count = 1

  enable_non_ssl_port           = false
  minimum_tls_version           = "1.2"
  public_network_access_enabled = true

  redis_configuration {
    enable_authentication = true
    maxmemory_policy      = "volatile-lru"
  }
}

resource "azurerm_redis_cache" "fail" {
  name                = "timeout-redis"
  location            = "West Europe"
  resource_group_name = azurerm_resource_group.example_rg.name
  subnet_id           = azurerm_subnet.example_redis_snet.id

  family      = "P"
  capacity    = 1
  sku_name    = "Premium"
  shard_count = 1

  enable_non_ssl_port           = false
  minimum_tls_version           = "1.1"
  public_network_access_enabled = true

  redis_configuration {
    enable_authentication = true
    maxmemory_policy      = "volatile-lru"
  }
}
resource "azurerm_redis_cache" "fail2" {
  name                = "timeout-redis"
  location            = "West Europe"
  resource_group_name = azurerm_resource_group.example_rg.name
  subnet_id           = azurerm_subnet.example_redis_snet.id

  family      = "P"
  capacity    = 1
  sku_name    = "Premium"
  shard_count = 1

  enable_non_ssl_port           = false
  public_network_access_enabled = true

  redis_configuration {
    enable_authentication = true
    maxmemory_policy      = "volatile-lru"
  }
}