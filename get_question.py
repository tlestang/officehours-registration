import requests

# Setting user Parameters
with open("qualtrics_token.txt", "r") as f:
    apiToken = f.read()

dataCenter = "fra1"

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
