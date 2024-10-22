description = ""
name        = "cron-poll"
stages = [
  {
    name = "Source"
    action = [{
      name     = "Source"
      category = "Source"
      owner    = "AWS"
      provider = "CodeCommit"
      version  = "1"
      configuration = {
        BranchName           = "master"
        PollForSourceChanges = "false"
        RepositoryName       = "cron-poll"
      }
      input_artifacts  = []
      output_artifacts = ["SourceArtifact"]
      run_order        = 1
    }]
  },
  {
    name = "Build"
    action = [{
      name             = "Build"
      category         = "Build"
      owner            = "AWS"
      provider         = "CodeBuild"
      input_artifacts  = ["SourceArtifact"]
      output_artifacts = ["BuildArtifact"]
      version          = "1"
      run_order        = 2
      configuration = {
        ProjectName = "cron-poll"
      }
    }]
  },
  {
    name = "Deploy"
    action = [{
      name             = "Deploy"
      category         = "Deploy"
      owner            = "AWS"
      provider         = "ECS"
      version          = "1"
      input_artifacts  = ["BuildArtifact"]
      output_artifacts = []
      configuration = {
        ClusterName = "test"
        ServiceName = "cron-poll"
      }
      run_order = 4
    }]
  }
]

common_tags = {
  name   = "aws-codebuild-container"
  module = "JamesWoolfenden/codepipeline/aws"
}