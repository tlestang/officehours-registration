from datetime import datetime, timedelta
import json
import re
import requests


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
        re.search(r"\d\d-\d\d-\d\d\d\d", time_slot).group(), "%d-%m-%Y"
    )
    start = datetime.combine(date, starttime)
    end = datetime.combine(date, endtime)

    # The time slot string also contains information about the room
    if "Online" in time_slot:
        room = None
    else:
        room = re.search(r"CAGB-\d\d-\d\d\d", time_slot).group()
    return email, start, end, room, pb_description


def getReponse(d, data_center, api_token):
    responseId = d["ResponseID"]
    surveyId = d["SurveyID"]
    headers = {
        "content-type": "application/json",
        "x-api-token": api_token,
    }

    url = "https://{0}.qualtrics.com/API/v3/surveys/" "{1}/responses/{2}".format(
        data_center, surveyId, responseId
    )

    rsp = requests.get(url, headers=headers)
    return rsp.json()


def update_available_slots(date, next_date, apiToken, dataCenter, surveyId, questionID):
    nchoices = 4
    slot_duration = timedelta(minutes=20)
    break_duration = timedelta(minutes=5)
    start = date[0]

    with open("data/template_question.json", "r") as f:
        content = json.load(f)

    for key in [str(i) for i in range(1, nchoices + 1)]:
        end = start + slot_duration
        choice_display = (
            f"{start:%H}:{start:%M} - {end:%H}:{end:%M}"
            f" ({date[0]:%d-%m-%Y}, {date[1]})"
        )
        content["Choices"][key]["Display"] = choice_display
        start = end + break_duration

    session_full_msg = (
        "There are no slots remaining for this session."
        f" The next session is planned for {next_date[0]}."
        f" Sign up will open on {date[0]:%d:%m:%Y} at {date[0]:%H:%M}."
    )
    content["Choices"][str(nchoices + 2)]["Display"] = session_full_msg

    baseUrl = (
        "https://{0}.qualtrics.com/API/v3/survey-definitions/"
        "{1}/questions/{2}".format(dataCenter, surveyId, questionID)
    )

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "x-api-token": apiToken,
    }
    r = requests.put(baseUrl, json=content, headers=headers)
    if r.status_code != requests.codes.ok:
        return r.json()
    return None


def update_survey_name_and_status(date, apiToken, dataCenter, surveyId):
    survey_name = (
        f"RSE office hours - {date[0].date()}"
        f" ({date[0]:%H:%M} - {date[0] +  timedelta(minutes=95):%H:%M},"
        f" {date[1]})"
    )

    data = {
        "name": survey_name,
        "isActive": True,
        "expiration": {
            # Qualtrics API expects times in UTC
            # https://en.wikipedia.org/wiki/List_of_military_time_zones
            "startDate": datetime.now().isoformat() + "Z",
            "endDate": date[0].isoformat() + "Z",
        },
    }

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "x-api-token": apiToken,
    }

    baseUrl = "https://{0}.qualtrics.com/API/v3/" "surveys/{1}".format(
        dataCenter, surveyId
    )
    r = requests.put(baseUrl, json=data, headers=headers)
    if r.status_code != requests.codes.ok:
        return r.json()
    return None


def list_quota_by_id(SurveyID, apiToken, dataCenter):
    url = (
        f"https://{dataCenter}.qualtrics.com/API/v3/survey-definitions/"
        f"{SurveyID}/quotas"
    )
    headers = {"Content-Type": "application/json", "X-API-TOKEN": apiToken}
    r = requests.get(url, headers=headers).json()
    return r["result"]["elements"]


def reset_quota(quota_data, SurveyID, apiToken, dataCenter):
    quota_data["Count"] = 0
    headers = {"Content-Type": "application/json", "X-API-TOKEN": apiToken}
    quotaID = quota_data["ID"]
    url = (
        f"https://{dataCenter}.qualtrics.com/API/v3/survey-definitions/"
        f"{SurveyID}/quotas/{quotaID}"
    )
    r = requests.put(url, json=quota_data, headers=headers)
    if r.status_code != requests.codes.ok:
        return r.json()
    return None
