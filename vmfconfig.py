import os


def get_account_creds():
    username = os.environ.get("VMF_USERNAME")
    api_token = os.environ.get("JENKINS_API_TOKEN")
    if not username:
        print("No username found in env")
        username = input("Username: ")
    if not api_token:
        print("No api key found in env")
        if not api_token:
            api_token = input("Api token: ")

    return username, api_token

