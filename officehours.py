import os
import requests
import json
from datetime import datetime, timedelta

datelist = [
    "2023-04-17T11:00:00",
    "2023-04-26T11:00:00",
    "2023-05-03T11:00:00",
    "2023-05-10T14:00:00",
]
dates = [datetime.fromisoformat(d) for d in datelist]
next_date_index, next_date = find_gt(dates, datetime.today())

nchoices = 4
slot_duration = timedelta(minutes=20)
break_duration = timedelta(minutes=5)
start = next_date

with open("data/template_question.json", "r") as f:
    content = json.load(f)

for key in [str(i) for i in range(1, nchoices + 1)]:
    end = start + slot_duration
    choice_display = (
        f"{start:%H}:{start:%M} - {end:%H}:{end:%M}"
        f" ({next_date:%d-%m-%Y})"
    )
    content["Choices"][key]["Display"] = choice_display
    start = end + break_duration

session_full_msg = (
    "There are no slots remaining for this session."
    f" The next session is planned for {dates[next_date_index + 1].date()}."
    f" Sign up will open on {next_date.date()} at {next_date:%H:%M}."
)
content["Choices"][str(nchoices + 2)]["Display"] = session_full_msg


# Setting user Parameters
apiToken = "RJOnyexfPXTG1SGp0izgJeliuhj67dn08NOZzqaM"
dataCenter = "fra1"

# Survey parameters
surveyId = "SV_8o95nhN17cI6naK"
questionID = "QID3"

baseUrl = (
    "https://{0}.qualtrics.com/API/v3/survey-definitions/"
    "{1}/questions/{2}".format(dataCenter, surveyId, questionID)
    )

headers = {
   'accept': "application/json",
   'content-type': "application/json",
   "x-api-token": apiToken,
   }
response = requests.put(baseUrl, json=content, headers=headers)
print(response)


survey_name = (
    f"RSE office hours - {next_date.date()}"
    f" ({next_date:%H:%M} - {next_date +  timedelta(minutes=95):%H:%M})"
)

# Update survey name
data = {
    "name": survey_name,
    "isActive": True,
    "expiration": {
        "startDate": datetime.now().isoformat(),
        "endDate": next_date.isoformat(),
    }
}
baseUrl = "https://{0}.qualtrics.com/API/v3/surveys/{1}".format(dataCenter, surveyId)
response = requests.put(baseUrl, json=data, headers=headers)
print(response)
