from aws_cdk import core
from aws_cdk import aws_sqs as sqs
class SqsQueueWithKmsKeyStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create an SQS queue with KMS encryption
        queue = sqs.Queue(self, "MySqsQueue",
            encryption=sqs.QueueEncryption.KMS,
            visibility_timeout=300  # Other properties for the queue
        )

app = core.App()
SqsQueueWithKmsKeyStack(app, "SqsQueueWithKmsKeyStack")
app.synth()



class SqsQueueWithKmsKeyIdStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define an SQS queue with a specific KmsMasterKeyId
        queue = sqs.CfnQueue(self, "MySqsQueue",
            visibility_timeout=300  # Other properties for the queue
        )

app = core.App()
SqsQueueWithKmsKeyIdStack(app, "SqsQueueWithKmsKeyIdStack")
app.synth()
