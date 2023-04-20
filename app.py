# Based on example at
# https://api.qualtrics.com/ZG9jOjg3NzY3MQ-retrieve-survey-responses-in-real-time
# https://api.qualtrics.com/9c31e43fef682-create-subscription

import os
import sys
from urllib.parse import unquote

from flask import Flask, request
import requests


def parsey(c):
    x = c.decode().split("&")
    d = {}
    for i in x:
        a, b = i.split("=")
        d[a] = b
    d['CompletedDate'] = unquote(d['CompletedDate'])
    return d


def getReponse(d, data_center, api_token):
    responseId = d['ResponseID']
    surveyId = d['SurveyID']
    headers = {
        "content-type": "application/json",
        "x-api-token": api_token,
       }

    url = (
        "https://{0}.qualtrics.com/API/v3/surveys/"
        "{1}/responses/{2}".format(data_center, surveyId, responseId)
    )

    rsp = requests.get(url, headers=headers)
    return rsp.json()


app = Flask(__name__)


@app.route("/", methods=['GET', 'POST'])
def handle():
    if request.method == 'POST':
        d = parsey(request.get_data())
        try:
            apiToken = os.environ['APIKEY']
            dataCenter = os.environ['DATACENTER']
        except KeyError:
            print("set environment variables APIKEY and DATACENTER")
            sys.exit(2)

        return getReponse(d, dataCenter, apiToken)
    else:
        return "<p>Hello, World</p>"
