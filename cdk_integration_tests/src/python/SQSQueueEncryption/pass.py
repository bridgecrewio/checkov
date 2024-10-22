from aws_cdk import core
from aws_cdk import aws_sqs as sqs
from aws_cdk import aws_kms as kms
from aws_cdk import aws_cloudformation as cfn
class SqsQueueWithKmsKeyStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create a KMS key for encryption
        kms_key = kms.Key(self, "MyKmsKey", enable_key_rotation=True)

        # Create an SQS queue with KMS encryption
        queue = sqs.Queue(self, "MySqsQueue",
            encryption=sqs.QueueEncryption.KMS,
            encryption_master_key=kms_key,
            visibility_timeout=300  # Other properties for the queue
        )

app = core.App()
SqsQueueWithKmsKeyStack(app, "SqsQueueWithKmsKeyStack")
app.synth()



class SqsQueueWithKmsKeyIdStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define a custom KMS key
        kms_key = cfn.CfnCustomResource(self, "MyKmsKeyResource",
            service_token="arn:aws:lambda:<your-region>:<your-account>:function/<your-lambda-function>",
            # Add other properties as needed
        )

        # Define an SQS queue with a specific KmsMasterKeyId
        queue = sqs.CfnQueue(self, "MySqsQueue",
            kms_master_key_id=kms_key.get_att("KmsKeyId"),
            visibility_timeout=300  # Other properties for the queue
        )

app = core.App()
SqsQueueWithKmsKeyIdStack(app, "SqsQueueWithKmsKeyIdStack")
app.synth()
