# Results

## Scan outputs

After running a ``checkov`` command on a Terraform file or folder, the scan's results will print in your current session Checkov currently supports output in 3 common formats: CLI, JSON & JUnit XML. 



### CLI Output

Running a Checkov scan with no output parameter will result in a color-coded CLI print output.

```
checkov -d /user/tf
```

Each print includes a scan summary and detailed scan results following.

```
Passed Checks: 1, Failed Checks: 1, Suppressed Checks: 0

Check: "Ensure all data stored in the S3 bucket is securely encrypted at rest"
/main.tf:
	 Passed for resource: aws_s3_bucket.template_bucket 

Check: "Ensure all data stored in the S3 bucket is securely encrypted at rest"
/../regionStack/main.tf:
	 Failed for resource: aws_s3_bucket.sls_deployment_bucket_name       
```

### JSON Output

Running a Checkov scan with the JSON output parmeter (```-o json```) will result in JSON print output.

```
checkov -d /user/tf -o json
```

The print includes detailed structured data-blocks that contain exact references to code blocks, line ranges and resources scanned.

```json
{
    "results": {
        "passed_checks": [
            {
                "check_id": "BC_AWS_S3_14",
                "check_name": "Ensure all data stored in the S3 bucket is securely encrypted at rest",
                "check_result": "SUCCESS",
                "code_block": "",
                "file_path": "/main.tf",
                "file_line_range": "",
                "resource": "aws_s3_bucket.template_bucket"
            },
            {
                "check_id": "BC_AWS_S3_13",
                "check_name": "Ensure the S3 bucket has access logging enabled",
                "check_result": "SUCCESS",
                "code_block": "",
                "file_path": "/main.tf",
                "file_line_range": "",
                "resource": "aws_s3_bucket.template_bucket"
            }
                  ],
        "suppressed_checks": [],
        "parsing_errors": []
    },
    "summary": {
        "passed": 2,
        "failed": 0,
        "suppressed": 0,
        "parsing_errors": 0
    }
}
```

### JUnit XML

Running a Checkov scan with the JSON output parmeter (```-o junit```) will result in JUnit XML print output.

```
checkov -d /user/tf -o junit
```

This print also includes detailed structured data-blocks that contain exact references to code blocks, line ranges and resources scanned.

```
***TODO
```



## Next Steps

Explore the [Integrations](**TODO)

