# Variables declaration:

variable "pud_default_var" {
  default = "pud_default_value"
}

resource "random_string" "pud-random-str" {
  length           = 10
  special          = false
  numeric = false
}

# Case 1: Pass: 'secure_environment_variables' exists in 'container' block and just 'environment_variables' doesn't exist

resource "azurerm_container_group" "pass_1" {
  name                = "pud_pass_1_container"
  location            = var.pud_default_var
  resource_group_name = var.pud_default_var
  ip_address_type     = "Public"
  dns_name_label      = "aci-label"
  os_type             = "Linux"

  container {
    name   = "hello-world"
    image  = "mcr.microsoft.com/azuredocs/aci-helloworld:latest"
    cpu    = "0.5"
    memory = "1.5"

    ports {
      port     = 443
      protocol = "TCP"
    }
  }

  container {
    name   = "een_le_pa"
    image  = "mcr.microsoft.com/azuredocs/aci-tutorial-sidecar"
    cpu    = "0.5"
    memory = "1.5"

    secure_environment_variables = {
      SEC_CONT_PASS_1 = random_string.pud-random-str
    }
  }
}

# case 2: Pass: No environment variables exists

resource "azurerm_container_group" "pass_2" {
  name                = "pud_pass_2_container"
  location            = "westus2"
  resource_group_name = var.pud_default_var
  os_type             = "Linux"

  init_container {
    name   = "init-container"
    image  = "init-image:latest"
    cpu    = 0.5
    memory = 512

  }
}

# Case 3: Fail: 'environment_variables' exists in 'init_container' block

resource "azurerm_container_group" "fail_1" {
  name                = "pud_fail_1_container"
  location            = "westus2"
  resource_group_name = var.pud_default_var
  os_type             = "Linux"

  init_container {
    name   = "init-container"
    image  = "init-image:latest"
    cpu    = 0.5
    memory = 512


    environment_variables = {
      ENV_INIT_FAIL_1 = random_string.pud-random-str
    }

    secure_environment_variables = {
      SEC_INIT_FAIL_1 = random_string.pud-random-str
    }
  }
}

# Case 4: Fail: 'environment_variables' exists in 'container' block

resource "azurerm_container_group" "fail_2" {
  name                 = "pud_pass_2_container"
  location              = "westus2"
  resource_group_name    = var.pud_default_var
  os_type              = "Linux"

  init_container {
    name                  = "pud-init-container"
    image                 = "init-image:latest"
    cpu                    = 0.5
    memory                = 512

    secure_environment_variables = {
      SEC_INIT_FAIL_2               = random_string.pud-random-str
    }
  }

  container {
    name                  = "pud-container"
    image                 = "my-image:latest"
    cpu                    = 1
    memory                = 1024

    ports {
      port                  = 80
      protocol              = "TCP"
    }

    environment_variables = {
      ENV_CONT_FAIL_2             = random_string.pud-random-str
    }
  }
}

