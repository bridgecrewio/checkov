from aws_cdk import core
from aws_cdk import aws_codebuild as codebuild

class MyCodeBuildProjectStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define a CodeBuild project with S3 artifacts and encryption disabled
        my_project = codebuild.Project(
            self, 'MyCodeBuildProject',
            project_name='MyProject',
            source=codebuild.Source.git_hub(owner='owner', repo='repo'),
            artifacts=codebuild.Artifacts(
                type=codebuild.ArtifactsType.S3,
                encryption_disabled=True
            ),
            environment=codebuild.BuildEnvironment(build_image=codebuild.LinuxBuildImage.STANDARD_5_0),
        )

app = core.App()
MyCodeBuildProjectStack(app, "MyCodeBuildProjectStack")
app.synth()
