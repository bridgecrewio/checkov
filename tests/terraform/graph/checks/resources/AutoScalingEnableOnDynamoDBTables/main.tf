# pass

resource "aws_dynamodb_table" "pass" {
  name           = "user"
  hash_key       = "user-id"
  billing_mode   = "PROVISIONED"
  read_capacity  = 10
  write_capacity = 10

  attribute {
    name = "user-id"
    type = "S"
  }
}

resource "aws_appautoscaling_target" "pass" {
  resource_id        = "table/${aws_dynamodb_table.pass.name}"
  scalable_dimension = "dynamodb:table:ReadCapacityUnits"
  service_namespace  = "dynamodb"
  min_capacity       = 1
  max_capacity       = 15
}

resource "aws_appautoscaling_policy" "pass" {
  name               = "rcu-auto-scaling"
  service_namespace  = aws_appautoscaling_target.pass.service_namespace
  scalable_dimension = aws_appautoscaling_target.pass.scalable_dimension
  resource_id        = aws_appautoscaling_target.pass.resource_id
  policy_type        = "TargetTrackingScaling"

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "DynamoDBReadCapacityUtilization"
    }

    target_value       = 75
    scale_in_cooldown  = 300
    scale_out_cooldown = 300
  }
}

resource "aws_dynamodb_table" "pass_unset" {
  name           = "user"
  hash_key       = "user-id"
  read_capacity  = 10
  write_capacity = 10

  attribute {
    name = "user-id"
    type = "S"
  }
}

resource "aws_appautoscaling_target" "pass_unset" {
  resource_id        = "table/${aws_dynamodb_table.pass_unset.name}"
  scalable_dimension = "dynamodb:table:ReadCapacityUnits"
  service_namespace  = "dynamodb"
  min_capacity       = 1
  max_capacity       = 15
}

resource "aws_appautoscaling_policy" "pass_unset" {
  name               = "rcu-auto-scaling"
  service_namespace  = aws_appautoscaling_target.pass_unset.service_namespace
  scalable_dimension = aws_appautoscaling_target.pass_unset.scalable_dimension
  resource_id        = aws_appautoscaling_target.pass_unset.resource_id
  policy_type        = "TargetTrackingScaling"

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "DynamoDBReadCapacityUtilization"
    }

    target_value       = 75
    scale_in_cooldown  = 300
    scale_out_cooldown = 300
  }
}

resource "aws_dynamodb_table" "pass_on_demand" {
  name           = "user"
  hash_key       = "user-id"
  billing_mode   = "PAY_PER_REQUEST"

  attribute {
    name = "user-id"
    type = "S"
  }
}


# fail

resource "aws_dynamodb_table" "fail" {
  name           = "user"
  hash_key       = "user-id"
  billing_mode   = "PROVISIONED"
  read_capacity  = 10
  write_capacity = 10

  attribute {
    name = "user-id"
    type = "S"
  }
}

resource "aws_dynamodb_table" "fail_no_policy" {
  name           = "user"
  hash_key       = "user-id"
  billing_mode   = "PROVISIONED"
  read_capacity  = 10
  write_capacity = 10

  attribute {
    name = "user-id"
    type = "S"
  }
}

resource "aws_appautoscaling_target" "fail_no_policy" {
  resource_id        = "table/${aws_dynamodb_table.fail_no_policy.name}"
  scalable_dimension = "dynamodb:table:ReadCapacityUnits"
  service_namespace  = "dynamodb"
  min_capacity       = 1
  max_capacity       = 15
}

# unknown

resource "aws_appautoscaling_target" "ecs" {
  max_capacity       = 4
  min_capacity       = 1
  resource_id        = "service/clusterName/serviceName"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "ecs" {
  name               = "scale-down"
  policy_type        = "StepScaling"
  resource_id        = aws_appautoscaling_target.ecs.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs.scalable_dimension
  service_namespace  = aws_appautoscaling_target.ecs.service_namespace

  step_scaling_policy_configuration {
    adjustment_type         = "ChangeInCapacity"
    cooldown                = 60
    metric_aggregation_type = "Maximum"

    step_adjustment {
      metric_interval_upper_bound = 0
      scaling_adjustment          = -1
    }
  }
}