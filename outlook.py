import requests
import configparser
from graph import Graph


def init_graphclient():
    global graph
    config = configparser.ConfigParser()
    config.read(["config.cfg", "config.dev.cfg"])
    azure_settings = config["azure"]
    graph = Graph(azure_settings)


def get_outlook_token():
    global token
    token = graph.get_user_token()


def create_outlook_event(email, start, end, room, description):
    url = "https://graph.microsoft.com/v1.0/me/events"
    payload = {
        "Subject": "RSE Office hours",
        "body": {
            "contentType": "text",
            "content": description,
        },
        "start": {
            "dateTime": f"{start:%Y-%m-%dT%H:%M}",
            "timeZone": "Europe/London",
        },
        "end": {
            "dateTime": f"{end:%Y-%m-%dT%H:%M}",
            "timeZone": "Europe/London",
        },
        "attendees": [
            {"emailAddress": {"address": email}, "type": "required"},
            {
                "emailAddress": {
                    "address": "t.lestang@imperial.ac.uk",
                    "name": "Thibault Lestang",
                }
            },
        ],
    }

    if room:
        payload["location"] = {
            "displayName": room,
            "locationType": "default",
        }
    else:
        payload["isOnlineMeeting"] = True
        payload["onlineMeetingProvider"] = "teamsForBusiness"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    r = requests.post(url, headers=headers, json=payload)
    if r.status_code != requests.codes.created:
        return r.json()
    return f"Event created successfully for {email}.\n"
