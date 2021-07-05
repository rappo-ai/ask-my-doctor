import datetime
import os
from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
import json
from pymongo import MongoClient 
 
def insert_token():
    # Making Connection
    myclient = MongoClient("mongodb://mongo:27017/") 
    
    # database 
    db = myclient["credentialsDB"]
    
    # Created or Switched to collection 
    # names: GeeksForGeeks
    Collection = db["patient"]
    
    # Loading or Opening the json file
    with open('cred.json') as file:
        file_data = json.load(file)
        
    # Inserting the loaded data in the Collection
    # if JSON contains data more than one entry
    # insert_many is used else inser_one is used
    if isinstance(file_data, list):
        Collection.insert_many(file_data)  
    else:
        Collection.insert_one(file_data)
    print('successfully inserted to DB')
 
def Create_Service():
    CLIENT_SECRET_FILE='cred.json'
    API_NAME='calendar'
    API_VERSION='v3'
    SCOPES =[ 'https://www.googleapis.com/auth/calendar.events','https://www.googleapis.com/auth/calendar']
    TOKEN_FILE='token.json'
    creds = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
        

        service = build(API_NAME,API_VERSION, credentials=creds)

        print(creds)
        print(API_SERVICE_NAME, 'service created successfully')
        return service



def convert_to_RFC_datetime(year=1900, month=1, day=1, hour=0, minute=0):
    dt = datetime.datetime(year, month, day, hour, minute, 0).isoformat() + 'Z'
    print('rfc',dt)
    return dt
