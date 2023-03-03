resource "azurerm_spring_cloud_container_deployment" "example" {
  name                = "example"
  spring_cloud_app_id = azurerm_spring_cloud_app.example.id
  instance_count      = 2
  arguments           = ["-cp", "/app/resources:/app/classes:/app/libs/*", "hello.Application"]
  commands            = ["java"]
  server              = "docker.io"
  image               = "springio/gs-spring-boot-docker"
  language_framework  = "springboot"

  environment_variables = {
    "Foo" : "Bar"
    "Env" : "Staging"
  }
}
