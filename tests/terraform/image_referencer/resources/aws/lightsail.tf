resource "aws_lightsail_container_service" "example" {
  name        = "example"
  power       = "nano"
  scale       = 1
  is_disabled = false
}

resource "aws_lightsail_container_service_deployment_version" "example" {
  container {
    container_name = "hello-world"
    image          = "amazon/amazon-lightsail:hello-world"

    command = []

    environment = {
      MY_ENVIRONMENT_VARIABLE = "my_value"
    }

    ports = {
      80 = "HTTP"
    }
  }

  public_endpoint {
    container_name = "hello-world"
    container_port = 80

    health_check {
      healthy_threshold   = 2
      unhealthy_threshold = 2
      timeout_seconds     = 2
      interval_seconds    = 5
      path                = "/"
      success_codes       = "200-499"
    }
  }

  service_name = aws_lightsail_container_service.example.name
}
