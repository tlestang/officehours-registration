import os
import requests
import json
from datetime import datetime, timedelta
from bisect import bisect_right


def find_gt(a, x):
    'Find leftmost value greater than x'
    i = bisect_right(a, x)
    if i != len(a):
        return a[i]
    raise ValueError


dates = [
    "2023-04-17T11:00:00",
    "2023-04-26T11:00:00",
    "2023-05-03T11:00:00",
    "2023-05-10T14:00:00",
]

next_date = find_gt(
    [datetime.fromisoformat(d) for d in dates], datetime.today()
)

nchoices = 4
choices_dict = {str(i): {} for i in range(1, nchoices + 1)}
slot_duration = timedelta(minutes=20)
break_duration = timedelta(minutes=5)
start = next_date
for key in choices_dict:
    end = start + slot_duration
    choices_dict[key] = {"Display": "{0:%H}:{0:%M} - {1:%H}:{1:%M}".format(start, end)}
    start = end + break_duration

with open("data/template_survey.json", "r") as f:
    content = json.load(f)


def get_question_dict(qid, content):
    qindex = [
        d["PrimaryAttribute"] for d in content["SurveyElements"]
    ].index(qid)
    return content["SurveyElements"][qindex]


def update_question_dict(qid, content, qdict):
    qindex = [
        d["PrimaryAttribute"] for d in content["SurveyElements"]
    ].index(qid)
    content["SurveyElements"][qindex] = qdict


survey_name = (
    f"RSE office hours - {next_date.date()}"
    f" ({next_date:%H:%M} - {next_date +  timedelta(minutes=95):%H:%M})"
)
content["SurveyEntry"]["SurveyName"] = survey_name
qdict = get_question_dict("QID3", content)
qdict["Payload"]["Choices"] = choices_dict
update_question_dict("QID3", content, qdict)

with open("newsurvey.qsf", "w") as f:
    json.dump(content, f)


# Setting user Parameters
apiToken = "RJOnyexfPXTG1SGp0izgJeliuhj67dn08NOZzqaM"
dataCenter = "fra1"

baseUrl = "https://{0}.qualtrics.com/API/v3/surveys".format(dataCenter)
headers = {
    "x-api-token": apiToken,
    }

files = {
    'file': ('newsurvey.qsf', open('newsurvey.qsf', 'rb'), 'application/vnd.qualtrics.survey.qsf')
  }

data = {"name": survey_name}
response = requests.post(baseUrl, files=files, data=data, headers=headers)
print(response.text)
