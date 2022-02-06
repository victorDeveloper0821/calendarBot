from __future__ import print_function

import datetime
import os.path
import httplib2
import configParser
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
Config = configParser.getConfigs()
CLIENT_SECRET=Config['Google']['SecretFile']

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
STORAGE = Storage('credentials.storage')
calendarId = Config['Google']['calendarId']
# run authorize credentials
def authorize_credentials():
# Fetch credentials from storage
    cred = STORAGE.get()
# If the credentials doesn't exist in the storage location then run the flow
    if cred is None or cred.invalid:
        flow = flow_from_clientsecrets(CLIENT_SECRET, scope=SCOPES)
        http = httplib2.Http()
        cred = run_flow(flow, STORAGE, http=http)
    return cred

def getEvents():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = authorize_credentials()
    try:
        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        timeDelta = datetime.timedelta(days=84);
        future = (datetime.datetime.utcnow() + timeDelta).isoformat() + 'Z'
        print('Getting the upcoming 10 events')
        # setting into config files
        events_result = service.events().list(calendarId=calendarId, timeMin=now,timeMax=future,
#                                               maxResults=20, 
                                                singleEvents=True,orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
            return
        else: 
            return events        

    except HttpError as error:
        print('An error occurred: %s' % error)

def classifyEvents(eventlist):
    # dictionary
    jsonMap = dict()
    jsonMap['Host']=excludeCancelDate(reduceList(classifyList(events,'Host')))
    jsonMap['Speaker']=excludeCancelDate(reduceList(classifyList(events,'Speaker')))
    jsonMap['Gourmet']=excludeCancelDate(reduceList(classifyList(events,'Gourmet')))
    
    return jsonMap    

def classifyList(eventList, position):
    return {
     'Host' :list(filter(lambda x: x['summary'].startswith('H-'),eventList)),
     'Speaker':list(filter(lambda x: x['summary'].startswith('S-'),eventList)),
     'Gourmet':list(filter(lambda x: x['summary'].startswith('G-'),eventList)),
     'cancelled':list(filter(lambda x: 'Cancelled' in x['summary'],eventList))
    }.get(position)

def reduceList(eventlst):
    available = list(map(lambda x: x['start'].get('date'),eventlst))
    return available

def saturdayLst():
    now = datetime.date.today()
    diff = datetime.timedelta(days=(5-now.weekday()))
    saturday = now + diff
    lst = []
    cancelDate = reduceList(classifyList(events,'cancelled'))
    for x in range(0,12):
        dateStr = (saturday+datetime.timedelta(days=x*7)).isoformat()
        if not dateStr in cancelDate:
            lst.append(dateStr)

    return lst
def excludeCancelDate(available):
    openDates = saturdayLst()
    dateList = []
    for dates in openDates:
        if dates not in available:
            dateList.append(dates)
    return dateList

if __name__ == '__main__':
    events = getEvents()
    """
    if not events:
        print("No events found")
    else: 
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])
    """    
    jsnMap = classifyEvents(events)
    print(jsnMap)
    #print(saturdayLst())
    #print(reduceList(classifyList(events,'cancelled')))

