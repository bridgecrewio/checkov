import os
import json
import datetime
import requests
import logging
import boto3
import random
import string

def getRandomString(length):
    # Random string with the combination of lower and upper case
    letters = string.ascii_letters
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str + str(random.randint(0,9))

def signup(event, context):
    bc_api_url = os.environ["BC_API_URL"]
    bc_user_pool = os.environ["BC_USER_POOL"]
    bc_user_pool_client_id = os.environ["BC_USER_POOL_CLIENT_ID"]
    bc_dashboard_url = os.environ["BC_DASHBOARD_URL"]

    signupUrl = "{}/signup".format(bc_api_url)
    postData = json.loads(event["body"])

    userEmail = postData["email"]
    orgName = postData["email"].split("@")[0]
    print(orgName)
    print(userEmail)
    customerName = orgName


    signupPayload = {
        "customer_name": orgName,
        "org_name": orgName,
        "org_name_display": orgName,
        "owner_email": userEmail,
        "owner_first_name":"Checkov",
        "owner_last_name":"User",
        "owner_phone":"+441234567890"
    }

    signupHeaders = {
    'Accept': 'application/json, text/plain, */*',
    'User-Agent': 'Mozilla/5.0 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36',
    'Content-Type': 'application/json;charset=UTF-8'
    }

    response = requests.request("POST", signupUrl, headers=signupHeaders, json=signupPayload)

    print(response.text.encode('utf8'))
    if response.status_code == 200:
        # Created platform user sucessfully. Now to get API Token
        # Set the users password, disabling the change password prompt at login (better UX).
        # Then, auth to cognito using the known creds to get the users JWT. Use this to call the intergrations/ApiToken endpoint. Return details to checkov along with user's password and JWT.
        idpClient = boto3.client('cognito-idp', region_name='us-west-2', aws_access_key_id=os.environ["Z_AWS_ACCESS_KEY_ID"],aws_secret_access_key=os.environ["Z_AWS_SECRET_ACCESS_KEY"])
        userPassword = getRandomString(8)
        changePasswordResponse = idpClient.admin_set_user_password(
            UserPoolId=bc_user_pool,
            Username=userEmail,
            Password=userPassword,
            Permanent=True
        )

        userAuthResponse = idpClient.admin_initiate_auth(
            UserPoolId=bc_user_pool,
            ClientId=bc_user_pool_client_id,
            AuthFlow='ADMIN_NO_SRP_AUTH',
            AuthParameters={
                'USERNAME': userEmail,
                'PASSWORD': userPassword
            }
        )


        apiTokenUrl = "{}/integrations/apiToken".format(bc_api_url)
        apiTokenPayload = {}
        ApiTokenHeaders = {
        'Accept': 'application/json',
        'Authorization': "{}".format(userAuthResponse["AuthenticationResult"]["IdToken"]),
        'User-Agent': 'Mozilla/5.0 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36'
        }

        apiTokenResponse = requests.request("GET", apiTokenUrl, headers=ApiTokenHeaders, data = apiTokenPayload)
        print(apiTokenUrl)
        print(ApiTokenHeaders)
        print(apiTokenResponse.json())
        print(userPassword)
        print(userAuthResponse)
        print("data:")
        print(apiTokenResponse.json()["data"])
        apiToken = apiTokenResponse.json()["data"]

        returnUserDetails = {
            "userEmail": userEmail,
            "userPassword": userPassword,
            "userJWT": userAuthResponse["AuthenticationResult"]["IdToken"],
            "userApiToken": apiToken,
            "dashboardURL": bc_dashboard_url
        }

        print(json.dumps(returnUserDetails)):

        response = {
            "statusCode": 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': 'true',
                'Access-Control-Allow-Headers': '*'
            },
            "body": json.dumps(returnUserDetails)
        }
        return response

    else:
        response = {
            "statusCode": 500,
            'headers': {
                'Content-Type': 'text/plain',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': 'true',
                'Access-Control-Allow-Headers': '*'
            },
            "body": "Failed to create platform user! Sorry!"
        }
        return response