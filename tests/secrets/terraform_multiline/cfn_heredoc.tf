resource "aws_cloudformation_stack" "lambda" {
  name = "lambda"

  parameters = {
    VPCCidr = "10.0.0.0/16"
  }

  template_body = <<STACK
AWSTemplateFormatVersion: '2010-09-09'
Description: VPC function.
Resources:
  Function:
    Type: AWS::Lambda::Function
    Properties:
      Handler: index.handler
      Role: arn:aws:iam::123456789012:role/lambda-role
      Code:
        S3Bucket: my-bucket
        S3Key: function.zip
      Runtime: nodejs12.x
      Timeout: 5
      TracingConfig:
        Mode: Active
      VpcConfig:
        SecurityGroupIds:
          - sg-085912345678492fb
        SubnetIds:
          - subnet-071f712345678e7c8
          - subnet-07fd123456788a036
      Tags:
        - Key: "SOME_NAME"
          Value: "some_value"
          # name1 & value1 are not valid arguments
        - Value: "Zo5Zhexnf9TUggdn+zBKGEkmUUvuKzVN+/fKPaMBA4zVyef4irH5H5YfwoC4IqAX0DNoMD12yIF67nIdIMg13atW4WM33eNMfXlE"
          Key: "TEST_PASSWORD_1"
          Key1: "TEST_PASSWORD_2"
          Value1: "1Vab3xejyUlh89P6tUJNXgO4t07DzmomF4tPBwTbwt+sjXHg3G0MPMRpH/I2ho4gS5H3AKJkvJZj87V7/Qnp/rHdbMVYK1F0BX35"
        - Key: "TEST_PASSWORD_3"
          # comment 1
          # comment 2
          # comment 3
          Value: "PtpfIZR+zZGPUWUYvLojqylVeEg63CBYN0FpGJ4yuH+9YxZZe8Uq7drEoTSfL64kElPEnVJk+H7SZr+wBoxN5qDWsbDmmUS2H76h"
        - Value: "emDJTiv6H/hP6I8Tmr5+kUdpBIQDrXMwFO7AkmbwROf3rM6uNToJlIJW7H5ApfPmSGU0oWBwflV6Cd9pPu5nEvgxt4YMHZ0SQ85z"
          # comment 1
          Key: "TEST_PASSWORD_4"
        - Key: "TEST_PASSWORD_LONG_1"
          Value: "m9+1ONt6FdpnByhlaKDwZ/jjA5gaPzrKY9q5G8cr6kjn092ogigwEOGGryjDqq/NkX1DnKGGG7iduJUJ48+Rv0tgpdVAxwLQuiszRnssmi2ck/Zf1iDFlNQtiE8rvXE6OTCsb6mrpyItLOVnEwsRSpggyRa3KLSuiguiZsK5KyXQ6BsiAclpLvz6QFBQoQkZNxownQrqgLwVwkK1gW0/EEm0m1ylz20ZeLgYO6tRSvKDW0lrgAI7g60F7/eJGv1UqQlxK58T+7u1UX/K11Q69e9jJE+LkQ932eY37U70oVbBVchHwSFKUoffernEaG9XP1tyEpIptPqVpcS2BMpktoR1p1yyWuxC5GsPc2RlPQzEbs3n5lPPnC/uEVu7/cJENSw5+9DzigiHYPz1Cq/p5HedIl5ysn2U2VFgHWekGBYin6ytfmF2Sx+hYqeRd6RcxyU434CXspWQqc330sp9q7vwPQHNecBrvG2Iy7mqVSvaJDnkZ8AN"
        - Key: "TEST_PASSWORD_no_password"
          Value: "RandomP@ssw0rd"
STACK
}
