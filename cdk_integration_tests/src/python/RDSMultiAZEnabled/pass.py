from aws_cdk import core
from aws_cdk import aws_rds as rds

class MyDBInstanceStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define RDS DB instance
        my_db_instance = rds.CfnDBInstance(
            self, 'MyDBInstance',
            engine='mysql',  # Change this to your desired engine type
            db_instance_class='db.t2.micro',
            allocated_storage=20,
            multi_az=True,
            # Other properties for your DB instance
        )

app = core.App()
MyDBInstanceStack(app, "MyDBInstanceStack")
app.synth()
