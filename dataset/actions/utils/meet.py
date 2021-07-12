from copy import deepcopy
import datetime
import os

from actions.utils.debug import is_debug_env
from actions.utils.host import get_host_url

API_NAME = "calendar"
API_VERSION = "v3"
AUTHORIZATION_BASE_URL = "https://accounts.google.com/o/oauth2/auth"
CALENDAR_ID = "primary"
CONFERENCE_DATA_VERSION = 1
HANGOUTS_MEET = "hangoutsMeet"
MOCK_HANGOUT_LINK = "https://meet.google.com/ejd-oszg-vrk"
REDIRECT_URI_DEBUG = "http://localhost:5005/webhooks/telegram/oauth"
SCOPES = [
    "https://www.googleapis.com/auth/calendar.events",
]
SEND_UPDATES = "all"


def get_google_auth_url(user_id):
    client_id = os.getenv("GOOGLE_OAUTH_CLIENT_ID")

    if not client_id:
        return AUTHORIZATION_BASE_URL

    from requests_oauthlib import OAuth2Session

    if is_debug_env():
        redirect_uri = REDIRECT_URI_DEBUG
    else:
        redirect_uri = get_host_url("/webhooks/telegram/oauth")

    google = OAuth2Session(client_id, scope=SCOPES, redirect_uri=redirect_uri)

    authorization_url, state = google.authorization_url(
        AUTHORIZATION_BASE_URL, state=user_id, access_type="offline", prompt="consent"
    )

    return authorization_url


def create_meeting(credentials, guest_emails, title, start_date, end_date, requestId):

    client_id = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET")

    if not (client_id and client_secret):
        return {"hangoutLink": MOCK_HANGOUT_LINK}

    from googleapiclient.discovery import build
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request

    google_oauth_credentials = deepcopy(credentials)
    google_oauth_credentials["client_id"] = client_id
    google_oauth_credentials["client_secret"] = client_secret

    creds = Credentials.from_authorized_user_info(
        google_oauth_credentials, scopes=SCOPES
    )
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

    service = build(API_NAME, API_VERSION, credentials=creds)

    event = {
        "summary": title,
        "start": {"dateTime": start_date.isoformat(sep="T")},
        "end": {
            "dateTime": end_date.isoformat(sep="T"),
        },
        "attendees": [{"email": x} for x in guest_emails],
        "conferenceData": {
            "createRequest": {
                "requestId": requestId,
                "conferenceSolutionKey": {"type": HANGOUTS_MEET},
            }
        },
        "reminders": {
            "useDefault": False,
        },
    }

    event = (
        service.events()
        .insert(
            calendarId=CALENDAR_ID,
            conferenceDataVersion=CONFERENCE_DATA_VERSION,
            sendUpdates=SEND_UPDATES,
            body=event,
        )
        .execute()
    )

    return event
