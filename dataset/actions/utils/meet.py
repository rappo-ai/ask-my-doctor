import datetime
import os
from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from actions.utils.helper import Create_Service,convert_to_RFC_datetime,insert_token

def get_google_auth_url(user_id):
    # #tbdemily
    # - create a webhook for oauth server redirect in dataset/connectors/telegram.py
    # - pass the url to this webhook in the below auth url (use get_host_url utility to get the full url with host name)
    # - cache user_id within the below oauth url
    # - in the webhook in dataset/connectors/telegram.py, set the incoming cached user_id as the sender_id
    # - in the webhook, trigger the intent /EXTERNAL_doctor_signup_google_authenticated{"credentials"="CREDS_FROM_GOOGLE"}
    return "https://accounts.google.com/o/oauth2/v2/auth"


def create_meeting(credentials, guest_emails, start_date, end_date):
    # tbdemily    
    insert_token()
    print(guest_emails)
    print(start_date)
    print(end_date)
    service=Create_Service()
    dt=convert_to_RFC_datetime()
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

