resource "aws_ecs_task_definition" "service01" {
  family = "service"
  container_definitions = jsonencode([
    merge(
      {
        name  = "first"
        image = "service-first"
      },
      {
        cpu       = 10
        memory    = 512
        essential = true
        portMappings = [
          {
            containerPort = 80
            hostPort      = 80
          }
        ]
      }
    )
  ])
  volume {
    name      = "service-storage"
    host_path = "/ecs/service-storage"
  }
}

resource "aws_ecs_task_definition" "service02" {
  family = "service"
  container_definitions = jsonencode([
    merge(
      {
        name  = "first"
        image = "service"
      },
      {
        cpu       = 10
        memory    = 512
        essential = true
        portMappings = [
          {
            containerPort = 80
            hostPort      = 80
          }
        ]
      }
    )
  ])
  volume {
    name      = "service-storage"
    host_path = "/ecs/service-storage"
  }
}