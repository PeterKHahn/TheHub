from apiclient.discovery import build
from httplib2 import Http

import json
import datetime
import dateutil.parser
import calendar



def add_to_calendar(creds, eventName, when):
    service = build('calendar', 'v3', credentials=creds)
    events = service.events()
    text = eventName + " " + when
    res = events.quickAdd(calendarId='primary', text=text).execute()

    return res['start']['dateTime']

def retrieve_calendar_events(creds, num):
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    service = build('calendar', 'v3', credentials=creds)
    events = service.events()
    res = events.list(calendarId='primary', timeMin=now, singleEvents=True,
        maxResults=num,  orderBy='startTime').execute()

    results = res.get('items', [])

    result = []
    last_day = ''
    event_list = []
    for event in results:
        start = event['start'].get('dateTime', event['start'].get('date'))
        start = dateutil.parser.parse(start)

        day = str(start.month) + "/" +str(start.day) + " : " + calendar.day_name[start.weekday()]


        if not day == last_day:

            last_day = day
            event_list = []
            result.append({
                "start" : day,
                "event_list" : event_list
            })
        event_list.append({
            "event" : event['summary'],
            "time" : str(start.time())[:-3]
        })


        #day += " " + str(start.time())[:-3]
        #result.append({"start":day, "event":event['summary']})
    return result
