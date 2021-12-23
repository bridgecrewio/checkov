# pass

resource "aws_neptune_cluster" "enabled" {
  cluster_identifier = "example"
  engine             = "neptune"

  storage_encrypted = true
}

# fail

resource "aws_neptune_cluster" "default" {
  cluster_identifier = "example"
  engine             = "neptune"
}

resource "aws_neptune_cluster" "disabled" {
  cluster_identifier = "example"
  engine             = "neptune"

  storage_encrypted = false
}
