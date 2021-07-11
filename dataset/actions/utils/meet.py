import datetime
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import os
from requests_oauthlib import OAuth2Session

from actions.utils.debug import is_debug_env
from actions.utils.host import get_host_url

API_NAME = "calendar"
API_VERSION = "v3"
AUTHORIZATION_BASE_URL = "https://accounts.google.com/o/oauth2/auth"
REDIRECT_URI_DEBUG = "http://localhost:5005/webhooks/telegram/oauth"
SCOPES = [
    "https://www.googleapis.com/auth/calendar",
]


def get_google_auth_url(user_id):
    client_id = os.getenv("GOOGLE_OAUTH_CLIENT_ID")

    if is_debug_env():
        redirect_uri = REDIRECT_URI_DEBUG
    else:
        redirect_uri = get_host_url("/webhooks/telegram/oauth")

    google = OAuth2Session(client_id, scope=SCOPES, redirect_uri=redirect_uri)

    authorization_url, state = google.authorization_url(
        AUTHORIZATION_BASE_URL, state=user_id, access_type="offline", prompt="consent"
    )

    return authorization_url


def create_meeting(credentials, guest_emails, start_date, end_date):

    client_id = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET")
    credentials["client_id"] = client_id
    credentials["client_secret"] = client_secret
    creds = Credentials.from_authorized_user_info(credentials, scopes=SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

    service = build(API_NAME, API_VERSION, credentials=creds)

    event = {
        "summary": "doctor meet",
        "start": {"dateTime": start_date.isoformat(sep="T")},
        "end": {
            "dateTime": end_date.isoformat(sep="T"),
        },
        "attendees": [
            {"email": guest_emails[0]},
        ],
        "conferenceData": {
            "createRequest": {
                "requestId": "zsd",
                "conferenceSolutionKey": {"type": "hangoutsMeet"},
            }
        },
    }

    conferenceDataVersion = 1
    sendUpdates = "all"

    event = (
        service.events()
        .insert(
            calendarId="primary",
            conferenceDataVersion=conferenceDataVersion,
            sendUpdates=sendUpdates,
            body=event,
        )
        .execute()
    )

    return {"link": event.get("hangoutLink")}
