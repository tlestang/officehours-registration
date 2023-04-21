# Based on example at
# https://api.qualtrics.com/ZG9jOjg3NzY3MQ-retrieve-survey-responses-in-real-time
# https://api.qualtrics.com/9c31e43fef682-create-subscription


import os
import sys

from flask import Flask, request, url_for, redirect

from find_next_sessions import find_next_two_dates
from qualtrics import (
    parsey, get_survey_response, update_available_slots,
    update_survey_name_and_status,
)
from outlook import (
    get_outlook_token, create_outlook_event, init_graphclient
)


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


@app.route("/update", methods=['POST'])
def update_survey():
    d = parsey(request.get_data())
    try:
        apiToken = os.environ["APIKEY"]
        dataCenter = os.environ["DATACENTER"]
    except KeyError:
        print("set environment variables APIKEY and DATACENTER")
        sys.exit(2)

    date, next_date = find_next_two_dates()
    r = update_available_slots(
        date, next_date,
        apiToken, dataCenter,
        surveyId=d["SurveyID"], questionID="QID3"
    )
    if r:
        return r
    r = update_survey_name_and_status(
        date, apiToken, dataCenter, surveyId=d["SurveyID"]
    )
    if r:
        return r
    else:
        return "Survey successfully updated.\n"

