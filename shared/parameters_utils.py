from functools import cache
import requests
import os
import tweepy

@cache
def get_parameter(name:str) -> str:
    url = f"http://localhost:2773/systemsmanager/parameters/get?name={name}"
    headers = {"X-Aws-Parameters-Secrets-Token": os.environ.get('AWS_SESSION_TOKEN')}
    response = requests.get(url, headers=headers)
    return response.json()["Parameter"]["Value"]

@cache
def get_secret_parameter(name:str) -> str:
    url = f"http://localhost:2773/secretsmanager/get?secretId={name}"
    headers = {"X-Aws-Parameters-Secrets-Token": os.environ.get('AWS_SESSION_TOKEN')}
    response = requests.get(url, headers=headers)
    return response.json()["SecretString"]