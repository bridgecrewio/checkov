resource "aws_ecs_service" "pass" {
  name    = "example"
  cluster = aws_ecs_cluster.example.id

  alarms {
    enable   = true
    rollback = true
    alarm_names = [
      aws_cloudwatch_metric_alarm.example.alarm_name
    ]
  }
}

resource "aws_ecs_service" "pass2" {
  name    = "example"
  cluster = aws_ecs_cluster.example.id

  alarms {
    enable   = true
    rollback = true
    alarm_names = [
      aws_cloudwatch_metric_alarm.example.alarm_name
    ]
  }
  network_configuration {
    subnets = []
    assign_public_ip = false
  }
}

resource "aws_ecs_service" "fail" {
  name    = "example"
  cluster = aws_ecs_cluster.example.id

  alarms {
    enable   = true
    rollback = true
    alarm_names = [
      aws_cloudwatch_metric_alarm.example.alarm_name
    ]
  }
  network_configuration {
    subnets = []
    assign_public_ip = true
  }
}