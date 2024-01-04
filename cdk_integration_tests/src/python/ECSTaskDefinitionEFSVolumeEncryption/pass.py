from aws_cdk import core
from aws_cdk import aws_ecs as ecs

class MyECSTaskDefinitionStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define ECS Task Definition with an EFS volume configuration and transit encryption disabled
        task_definition = ecs.CfnTaskDefinition(
            self, 'MyTaskDefinition',
            volumes=[
                {
                    'efs_volume_configuration': {
                        'transit_encryption': 'ENABLED'
                    }
                }
            ]
            # Other properties for your ECS Task Definition
        )

app = core.App()
MyECSTaskDefinitionStack(app, "MyECSTaskDefinitionStack")
app.synth()
