provider "aws" {
    region = "us-east-1"
}

provider "aws" {
    region = "us-east-2"
    alias = "ohio"
}
provider "aws" {
    region = "us-west-2"
    alias = "oregon"
}