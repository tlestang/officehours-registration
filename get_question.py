import os
import requests

# Setting user Parameters
apiToken = os.environ["APIKEY"]
dataCenter = os.environ["DATACENTER"]

surveyId = "SV_8o95nhN17cI6naK"
questionId = "QID3"

baseUrl = "https://{0}.qualtrics.com/API/v3/survey-definitions/{1}/questions/{2}".format(
    dataCenter, surveyId, questionId)

headers = {
   'accept': "application/json",
   'content-type': "application/json",
   "x-api-token": apiToken,
}

response = requests.get(baseUrl, headers=headers)

print(response.text)
