AWSTemplateFormatVersion: '2010-09-09'
Description: AWS CloudFormation Template to deploy insecure infrastructure

Resources:
  AnalysisLambda:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub "${AWS::AccountId}-${CompanyName}-${Environment}-analysis"
      Runtime: nodejs12.x
      Role: !GetAtt IAM4Lambda.Arn
      Handler: exports.test
      Code:
        ZipFile: |
          console.log("Hello World");
      Environment:
        Variables:
          access_key: "AKIAIOSFODNN7EXAMPLE"
          secret_key: "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
      Tags:
        - Key: Name
          Value: !Sub "${AWS::AccountId}-${CompanyName}-${Environment}-analysis"
        - Key: Environment
          Value: !Sub "${AWS::AccountId}-${CompanyName}-${Environment}"
