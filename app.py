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
    available_slots = rsp["result"]["labels"]["QID3_DO"]

    email = response_values["QID1_TEXT"]
    pb_description = response_values["QID4_TEXT"]
    time_slot = available_slots[response_values["QID3"]]

    # time_slot is a string of the form "HH:MM - HH:MM" so now we have
    # to parse it into two datetime.time instances
    s, e = re.findall(r"(\d\d):(\d\d)", time_slot)
    starttime = time(hour=int(s[0]), minute=int(s[1]))
    endtime = time(hour=int(e[0]), minute=int(e[1]))

    return email, starttime, endtime, pb_description


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


def get_event_date(path):
    def find_gt(a, x):
        "Find leftmost value greater than x"
        i = bisect_right(a, x)
        if i != len(a):
            return i, a[i]
        raise ValueError

    with open(path, "r") as f:
        dates = [datetime.fromisoformat(d.strip()) for d in f]

    _, date = find_gt(dates, datetime.today())
    return date


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

        (
            email,
            starttime,
            endtime,
            pb_description,
        ) = get_survey_response(
            d, dataCenter, apiToken, fp="data/template_survey_response.json"
        )

        date = get_event_date("dates.txt")
        meeting_info = (
            email,
            datetime.combine(date, starttime),
            datetime.combine(date, endtime),
            pb_description,
        )
        return create_outlook_event(*meeting_info)
    else:
        return "<p>Hello, World</p>"


@app.route("/auth")
def msgraph_authenticate():
    init_graphclient()
    get_outlook_token()

    return redirect(url_for("handle"))
