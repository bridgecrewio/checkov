# Variables declaration:

variable "pud_default_var" {
  default = "pud_default_value"
}

# Case 1: Pass: 'secure_environment_variables' exists in 'container' block

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
    name   = "sidecar"
    image  = "mcr.microsoft.com/azuredocs/aci-tutorial-sidecar"
    cpu    = "0.5"
    memory = "1.5"

    secure_environment_variables = {
      INIT_SECRET_VAR               = "secret_value"
    }
  }
}

# Case 2: Pass: 'secure_environment_variables' exists in 'init_container' block

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

    environment_variables = {
      INIT_PUBLIC_VAR = "public_value"
    }

    secure_environment_variables = {
      PUD_INIT_SECRET_VAR = "pud_secret_value"
    }
  }
}

# Case 3: Pass: 'secure_environment_variables' exists in 'container' or 'init_container' blocks

resource "azurerm_container_group" "pass_3" {
  name                 = "pud_pass_2_container"
  location              = "westus2"
  resource_group_name    = var.pud_default_var
  os_type              = "Linux"

  init_container {
    name                  = "pud-init-container"
    image                 = "init-image:latest"
    cpu                    = 0.5
    memory                = 512

    environment_variables = {
      INIT_PUBLIC_VAR             = "public_value"
    }

    secure_environment_variables = {
      PUD_INIT_SECRET_VAR               = "pud_secret_value"
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
      MY_PUBLIC_VAR             = "public_value"
    }

    secure_environment_variables = {
      PUD_SECRET_VAR               = "secret_value"
    }
  }
}

# case 4: Fail: 'secure_environment_variables' exists BUT, it's empty

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
      INIT_PUBLIC_VAR = "public_value"
    }

    secure_environment_variables = {

    }
  }
}

# case 5: Fail: 'secure_environment_variables' does NOT exist

resource "azurerm_container_group" "fail_2" {
  name                = "pud_fail_2_container"
  location            = "westus2"
  resource_group_name = var.pud_default_var
  os_type             = "Linux"

  init_container {
    name   = "init-container"
    image  = "init-image:latest"
    cpu    = 0.5
    memory = 512

    environment_variables = {
      PUD_INIT_PUBLIC_VAR = "public_value"
    }
  }
}