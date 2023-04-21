# Based on example at
# https://api.qualtrics.com/ZG9jOjg3NzY3MQ-retrieve-survey-responses-in-real-time
# https://api.qualtrics.com/9c31e43fef682-create-subscription

from datetime import datetime, time
import os
import re
import sys
from bisect import bisect_right
import json

from flask import Flask, request, url_for, redirect
import requests

from outlook import get_outlook_token, create_outlook_event, init_graphclient


def parsey(c):
    x = c.decode().split("&")
    d = {}
    for i in x:
        a, b = i.split("=")
        d[a] = b
    return d


def get_survey_response(d, data_center, api_token, fp=None):
    if fp:
        with open(fp, "r") as f:
            rsp = json.load(f)
    else:
        rsp = getReponse(d, data_center, api_token)

    response_values = rsp["result"]["values"]

    email = response_values["QID1_TEXT"]
    pb_description = response_values["QID4_TEXT"]
    time_slot = rsp["result"]["labels"]["QID3"]

    # time_slot is a string of the form "HH:MM - HH:MM" so now we have
    # to parse it into two datetime.time instances
    starttime, endtime = [
        datetime.strptime(s, "%H:%M").time()
        for s in re.findall(r"\d\d:\d\d", time_slot)
    ]
    date = datetime.strptime(
        re.search(r'\d\d-\d\d-\d\d\d\d', time_slot).group(),
        '%d-%m-%Y'
    )
    start = datetime.combine(date, starttime)
    end = datetime.combine(date, endtime)

    return email, start, end, pb_description


def getReponse(d, data_center, api_token):
    responseId = d["ResponseID"]
    surveyId = d["SurveyID"]
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
graph_token = None


@app.route("/", methods=["GET", "POST"])
def handle():
    if request.method == "POST":
        d = parsey(request.get_data())
        d["SurveyID"] = "SV_8o95nhN17cI6naK"
        try:
            apiToken = os.environ["APIKEY"]
            dataCenter = os.environ["DATACENTER"]
        except KeyError:
            print("set environment variables APIKEY and DATACENTER")
            sys.exit(2)

        meeting_info = get_survey_response(
            d, dataCenter, apiToken
        )

        return create_outlook_event(*meeting_info)
    else:
        return "<p>Hello, World</p>"


@app.route("/auth")
def msgraph_authenticate():
    init_graphclient()
    get_outlook_token()

    return redirect(url_for("handle"))
