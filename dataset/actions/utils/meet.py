import datetime
import os
from requests_oauthlib import OAuth2Session

from actions.utils.debug import is_debug_env
from actions.utils.helper import Create_Service, convert_to_RFC_datetime, insert_token
from actions.utils.host import get_host_url

REDIRECT_URI_DEBUG = "http://localhost:5005/webhooks/telegram/oauth"
AUTHORIZATION_BASE_URL = "https://accounts.google.com/o/oauth2/auth"
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
    # tbdemily
    insert_token()
    print(guest_emails)
    print(start_date)
    print(end_date)
    service = Create_Service()
    dt = convert_to_RFC_datetime()
    print(dt)
    # event = {
    # 'summary': 'doctor meet',
    # 'start': {
    #     'dateTime': convert_to_RFC_datetime(2021,6,30,2,20),
    # },
    # 'end': {
    #     'dateTime': convert_to_RFC_datetime(2021,6,30,3,20),
    # },
    # 'attendees': [
    #     {'email': 'emily_b180614cs@nitc.ac.in'},
    #     {'email': 'ey2anu@gmail.com'},
    # ],
    # 'conferenceData' : {
    #     'createRequest': {
    #     'requestId':'zsd',
    #     'conferenceSolutionKey' : {
    #         'type' : 'hangoutsMeet'
    #     }
    #     }
    # },
    # # 'reminders': {
    # #   'useDefault':True
    # # }
    # }

    # conferenceDataVersion= 1
    # sendUpdates='all'

    # event = service.events().insert(
    # calendarId='primary',
    # conferenceDataVersion=conferenceDataVersion,
    # sendUpdates=sendUpdates,
    # body=event
    # ).execute()

    # print(event)
    # id=event.get('id')
    # print (id)
    # print ('Event created: %s',event.get('hangoutLink'))

    # event_move_resp=service.events().move(
    # calendarId='primary',
    # eventId=id,
    # destination='ey2anu@gmail.com',
    # sendUpdates=sendUpdates
    # ).execute()

    # pprint(event_move_resp)

    # #tbdemily - create the google meet meeting using these credentials
    # - these credentials are same as those passed from webhook (see get_google_auth_url)
    return {"link": "https://meet.google.com/vix-uaxv-hcx"}
