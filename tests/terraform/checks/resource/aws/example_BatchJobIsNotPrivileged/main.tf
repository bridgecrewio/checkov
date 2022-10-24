resource "aws_batch_job_definition" "unknown2" {
  name                 = "foobar"
  type                 = "container"
  container_properties = file("${path.module}/job_definition.json")
}


resource "aws_batch_job_definition" "fail" {
  name = "tf_test_batch_job_definition"
  type = "container"

  container_properties = <<CONTAINER_PROPERTIES
{
    "command": ["ls", "-la"],
    "image": "busybox",
    "memory": 1024,
    "vcpus": 1,
    "privileged": true,
    "volumes": [
      {
        "host": {
          "sourcePath": "/tmp"
        },
        "name": "tmp"
      }
    ],
    "environment": [
        {"name": "VARNAME", "value": "VARVAL"}
    ],
    "mountPoints": [
        {
          "sourceVolume": "tmp",
          "containerPath": "/tmp",
          "readOnly": false
        }
    ],
    "ulimits": [
      {
        "hardLimit": 1024,
        "name": "nofile",
        "softLimit": 1024
      }
    ]
}
CONTAINER_PROPERTIES
}



resource "aws_batch_job_definition" "pass" {
  name = "tf_test_batch_job_definition"
  type = "container"

  container_properties = <<CONTAINER_PROPERTIES
{
    "command": ["ls", "-la"],
    "image": "busybox",
    "memory": 1024,
    "vcpus": 1,
    "privileged": false,
    "volumes": [
      {
        "host": {
          "sourcePath": "/tmp"
        },
        "name": "tmp"
      }
    ],
    "environment": [
        {"name": "VARNAME", "value": "VARVAL"}
    ],
    "mountPoints": [
        {
          "sourceVolume": "tmp",
          "containerPath": "/tmp",
          "readOnly": false
        }
    ],
    "ulimits": [
      {
        "hardLimit": 1024,
        "name": "nofile",
        "softLimit": 1024
      }
    ]
}
CONTAINER_PROPERTIES
}



resource "aws_batch_job_definition" "unknown" {
  name = "tf_test_batch_job_definition"
  type = "container"
}


resource "aws_batch_job_definition" "pass2" {
  name = "tf_test_batch_job_definition"
  type = "container"

  container_properties = <<CONTAINER_PROPERTIES
{
    "command": ["ls", "-la"],
    "image": "busybox",
    "memory": 1024,
    "vcpus": 1,
    "volumes": [
      {
        "host": {
          "sourcePath": "/tmp"
        },
        "name": "tmp"
      }
    ],
    "environment": [
        {"name": "VARNAME", "value": "VARVAL"}
    ],
    "mountPoints": [
        {
          "sourceVolume": "tmp",
          "containerPath": "/tmp",
          "readOnly": false
        }
    ],
    "ulimits": [
      {
        "hardLimit": 1024,
        "name": "nofile",
        "softLimit": 1024
      }
    ]
}
CONTAINER_PROPERTIES
}

resource "aws_batch_job_definition" "pass3" {
  name = "tf_test_batch_job_definition"
  type = "container"

  container_properties = jsonencode({
    "command" : ["ls", "-la"],
    "image" : "busybox",
    "memory" : 1024,
    "vcpus" : 1,
    "volumes" : [
      {
        "host" : {
          "sourcePath" : "/tmp"
        },
        "name" : "tmp"
      }
    ],
    "environment" : [
      { "name" : "VARNAME", "value" : "VARVAL" }
    ],
    "mountPoints" : [
      {
        "sourceVolume" : "tmp",
        "containerPath" : "/tmp",
        "readOnly" : false
      }
    ],
    "ulimits" : [
      {
        "hardLimit" : 1024,
        "name" : "nofile",
        "softLimit" : 1024
      }
    ]
  })
}

# not a valid configuration
resource "aws_batch_job_definition" "unknown3" {
  name = "tf_test_batch_job_definition"
  type = "container"

  container_properties = [{
    "image" : "busybox",
    "memory" : 1024,
    "vcpus" : 1,
  }]
}
