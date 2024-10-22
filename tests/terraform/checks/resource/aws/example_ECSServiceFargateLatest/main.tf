resource "aws_ecs_service" "pass" {
  name = "pike"
  launch_type = "FARGATE"
  platform_version = "LATEST"
}

resource "aws_ecs_service" "pass2" {
  name = "pike"
  launch_type = "FARGATE"
}

resource "aws_ecs_service" "fail" {
  name = "pike"
  launch_type = "FARGATE"
  platform_version = "1.4.0"
}

resource "aws_ecs_service" "unknown" {
  name = "pike"
  platform_version = "LATEST"
}

resource "aws_ecs_service" "unknown2" {
  name = "pike"
}