data "aws_iam_policy_document" "fail1" {
  statement {
    sid    = "sampleStatesGlobal"
    effect = "Allow"
    actions = [
      #"states:ListStateMachines", #ok  # "access_level": "List", "required": false
      #"states:ListActivities", #ok  # "access_level": "List", ""required": false"
      #"states:CreateStateMachine", #bad  # "access_level": "Write", "required": true, condition_keys, resource_types_lower_name
      #"states:CreateActivity", #bad  # "access_level": "Write", "required": true, condition_keys, resource_types_lower_name
      #"states:ListTagsForResource", #bad  # "access_level": "List", "required": false, resource_types, resource_types_lower_name
      "states:TagResource", #bad  # "access_level": "Tagging", "required": false, condition_keys, resource_types_lower_name
      "states:RedriveExecution", # expect fail resource_types_lower_name exists  # didn't fail
      "elemental-appliances-software:UntagResource"
    ]
    resources = ["*"]
  }

}

data "aws_iam_policy_document" "good1" {
  statement {
    sid    = "sampleStatesGlobal"
    effect = "Allow"
    actions = [
      #"states:ListStateMachines", #ok  # "access_level": "List", "required": false
      #"states:ListActivities", #ok  # "access_level": "List", ""required": false"
      "states:CreateStateMachine", #bad  # "access_level": "Write", "required": true, condition_keys, resource_types_lower_name
      #"states:CreateActivity", #bad  # "access_level": "Write", "required": true, condition_keys, resource_types_lower_name
      #"states:ListTagsForResource", #bad  # "access_level": "List", "required": false, resource_types, resource_types_lower_name
      #"states:TagResource", #bad  # "access_level": "Tagging", "required": false, condition_keys, resource_types_lower_name
      #"states:RedriveExecution", # expect fail resource_types_lower_name exists  # didn't fail
      #"elemental-appliances-software:UntagResource"
    ]
    resources = ["*"]
  }

}