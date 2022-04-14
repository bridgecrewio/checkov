resource "aws_ecs_task_definition" "pass" {
  family = "service"
  container_definitions = jsonencode([
    {
      name      = "first"
      image     = "service-first"
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
  ])
  execution_role_arn = "aws_iam_role.execution.arn"
  task_role_arn = "aws_iam_role.task.arn"
}

resource "aws_ecs_task_definition" "fail" {
  family = "service"
  container_definitions = jsonencode([
    {
      name      = "first"
      image     = "service-first"
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
  ])
  execution_role_arn = "aws_iam_role.example.arn"
  task_role_arn = "aws_iam_role.example.arn"
}