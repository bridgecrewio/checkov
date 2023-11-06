from aws_cdk import core
from aws_cdk import aws_kinesis as kinesis

class KinesisStreamStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create an Amazon Kinesis stream
        kinesis_stream = kinesis.CfnStream(
            self,
            "MyKinesisStream",
            name="my-kinesis-stream",
            shard_count=2,  # The number of shards in the stream
            stream_encryption={
                "encryption_type": "ABC",
                "key_id": "YOUR_KMS_KEY_ID"  # Replace with your KMS key ID
            }
        )

app = core.App()
KinesisStreamStack(app, "KinesisStreamStack")
app.synth()
