resource "aws_appautoscaling_target" "dynamoDB" {
  resource_id        = "table/${aws_dynamodb_table.example.name}"
  scalable_dimension = "dynamodb:table:ReadCapacityUnits"
  service_namespace  = "dynamodb"
  min_capacity       = 1
  max_capacity       = 15
}

resource "aws_appautoscaling_policy" "ok_connect_dynamo_table" {
  name               = "cpu-auto-scaling"
  service_namespace  = aws_appautoscaling_target.dynamoDB.service_namespace
  scalable_dimension = aws_appautoscaling_target.dynamoDB.scalable_dimension
  resource_id        = aws_appautoscaling_target.dynamoDB.resource_id
  policy_type        = "TargetTrackingScaling"

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "RDSReaderAverageCPUUtilization"
    }

    target_value       = 75
    scale_in_cooldown  = 300
    scale_out_cooldown = 300
  }
}

resource "aws_appautoscaling_target" "not_dynamo" {
  service_namespace  = "rds"
  scalable_dimension = "rds:cluster:ReadReplicaCount"
  resource_id        = "cluster:${aws_rds_cluster.example.id}"
  min_capacity       = 1
  max_capacity       = 15
}

resource "aws_appautoscaling_policy" "not_ok_connect_dynamo_table" {
  name               = "cpu-auto-scaling"
  service_namespace  = aws_appautoscaling_target.not_dynamo.service_namespace
  scalable_dimension = aws_appautoscaling_target.not_dynamo.scalable_dimension
  resource_id        = aws_appautoscaling_target.not_dynamo.resource_id
  policy_type        = "TargetTrackingScaling"

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "RDSReaderAverageCPUUtilization"
    }

    target_value       = 75
    scale_in_cooldown  = 300
    scale_out_cooldown = 300
  }
}