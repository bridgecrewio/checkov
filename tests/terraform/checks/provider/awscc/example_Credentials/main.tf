provider "awscc" {
    alias = "pass"
    region = "us-west-2"
}

provider "awscc" {
    alias = "fail"
    region     = "us-west-2"
    access_key = "AKIAIOSFODNN7EXAMPLE"
    secret_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
}

provider "awscc" {
    alias = "fail2"
    region     = "us-west-2"
    access_key = "AKIAIOSFODNN7EXAMPLE"
}

provider "awscc" {
    alias = "fail3"
    region     = "us-west-2"
    secret_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
}