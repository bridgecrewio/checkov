from aws_cdk import core
from aws_cdk import aws_glue as glue

class GlueCrawlerStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        crawler = glue.CfnCrawler(
            self,
            "MyCrawler",
            name="MyCrawler",
            database_name="mydatabase",
            role=crawler_role.role_arn,
            targets={
                "s3Targets": [
                    {
                        "path": "s3://your-s3-bucket/path/to/crawl",
                    }
                ]
            },
        )

app = core.App()
GlueCrawlerStack(app, "GlueCrawlerStack")
app.synth()


class GlueDevEndpointStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create an AWS Glue DevEndpoint
        dev_endpoint = glue.CfnDevEndpoint(
            self,
            "MyDevEndpoint",
            role_arn="arn:aws:iam::YOUR_ACCOUNT_ID:role/YourGlueDevEndpointRole",
            worker_type="Standard",
            glue_version="1.0",
        )

app = core.App()
GlueDevEndpointStack(app, "GlueDevEndpointStack")
app.synth()

class GlueJobStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create an AWS Glue Job
        job = glue.CfnJob(
            self,
            "MyGlueJob",
            command={
                "name": "glueetl",
                "pythonVersion": "3"
            },
            default_arguments={
                "--job-language": "python"
            },
            max_capacity=10,
            glue_version="1.0"
        )

app = core.App()
GlueJobStack(app, "GlueJobStack")
app.synth()

