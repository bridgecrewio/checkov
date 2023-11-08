from aws_cdk import core
from aws_cdk import aws_ecr as ecr

class MyECRStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create an ECR repository with immutable image tags
        ecr_repository = ecr.Repository(
            self,
            "MyECRRepository",
            repository_name="my-ecr-repo",
            image_tag_mutability=ecr.TagMutability.MUTABLE,  # Set image tag mutability to IMMUTABLE
        )
